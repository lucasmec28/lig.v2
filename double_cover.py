"""Ligação à alma de coluna com nervura, quatro horizontais e duas talas.

Modelo local por componentes. O equilíbrio é explícito; a validação do nó
tridimensional e da capacidade de rotação permanece uma pendência identificada.
Unidades internas: N, mm, MPa. Nenhuma majoração adicional de ações.
"""
from dataclasses import dataclass, asdict
import math
from .models import Profile, Check, Issue, Result, STEELS, BOLTS, DIAMETERS, VERSION, profiles, INTERFERENCE_ASSUMPTION
from .engine import bolt_shear, plate_ltb
from .local_checks import elastic_group, grip_factor

E=200000.;G1=1.1;G2=1.35
NBR='ABNT NBR 8800:2024, versão corrigida 2025'
ASSEMBLY_NOTE='A estabilidade acoplada e a capacidade de rotação do conjunto nervura–enrijecedores–coluna ainda não estão validadas para esta configuração com duas talas.'
PLATE_STOCK={'3/16"':4.7625,'1/4"':6.35,'5/16"':7.9375,'3/8"':9.525,'1/2"':12.7,'5/8"':15.875,'3/4"':19.05,'1"':25.4}


@dataclass(frozen=True)
class DoubleCoverConnection:
    beam: Profile
    support: Profile
    project: str='Viga na alma de coluna — duas talas'
    beam_steel: str='ASTM A572 Gr.50'
    support_steel: str='ASTM A572 Gr.50'
    fin_steel: str='ASTM A36'
    cover_steel: str='ASTM A36'
    stiffener_steel: str='ASTM A36'
    bolt: str='ASTM F3125 A325'
    db: float=19.05
    threads: bool=True
    n: int=3
    pitch: float=70.
    edge_v: float=40.
    edge_x: float=40.
    gap: float=10.
    extension: float=100.
    fin_t: float=7.9375
    cover_t: float=7.9375
    stiffener_t: float=9.525
    root_height: float=353.
    corner_clip: float=18.
    weld_web: float=5.
    weld_fin_stiffener: float=5.
    weld_stiffener_column: float=6.
    fw: float=485.
    clearance: float=10.
    tool_radius: float=18.
    shim_mode: str='automatic'
    fit_tolerance: float=1.
    drilled: bool=False
    norm_minimum: bool=True
    V: float=11000.
    N: float=2000.
    notes: str=''

    @property
    def hp(self):return 2*self.edge_v+(self.n-1)*self.pitch
    @property
    def plate_top(self):return (self.beam.d-self.hp)/2
    @property
    def dh(self):return self.db+(1.5875 if self.db<25.4 else 3.175)
    @property
    def dh_net(self):return self.dh+(0 if self.drilled else 2.)
    @property
    def projection(self):return (self.support.bf-self.support.tw)/2
    @property
    def fin_length(self):return self.projection+self.extension
    @property
    def pin_x(self):return self.fin_length+self.gap/2
    @property
    def group_e(self):return self.edge_x+self.gap/2
    @property
    def cover_length(self):return 4*self.edge_x+self.gap
    @property
    def thickness_difference(self):return abs(self.fin_t-self.beam.tw)
    @property
    def shim_each(self):return self.thickness_difference/2 if self.shim_mode=='automatic' else 0.
    @property
    def shim_side(self):return 'nervura' if self.fin_t<self.beam.tw else 'viga' if self.fin_t>self.beam.tw else 'nenhum'
    @property
    def stiffener_width(self):return self.projection
    @property
    def stiffener_span(self):return self.support.d-2*self.support.tf
    @property
    def fixed_assumptions(self):
        return {'rotation_reference':'mid_gap','symmetric_double_cover':True,'rows_equal_both_groups':True,
                'horizontal_stiffeners':4,'rear_stiffeners_strength_credit':False,'beam_effectively_restrained':True,
                'welded_profile_internal_joints':'complete_joint_penetration_matching_filler',
                'axial_sign':'positive_tension_negative_compression','external_moment_input':False,
                'support_load_path':'V_to_web_N_and_local_M_to_front_horizontal_pair',
                'assembly_stability_and_rotation':'not_validated','column_global_check':'external'}
    def to_dict(self):return {'schema_version':1,'connection_type':'column_web_double_cover','app_version':VERSION,'connection':asdict(self),'fixed_assumptions':self.fixed_assumptions}
    @staticmethod
    def from_dict(data):
        if not isinstance(data,dict) or data.get('connection_type')!='column_web_double_cover' or data.get('schema_version')!=1:
            raise ValueError('Selecione um projeto da ligação à alma de coluna com duas talas.')
        d=dict(data['connection']);d['beam']=Profile(**d['beam']);d['support']=Profile(**d['support'])
        return DoubleCoverConnection(**d)


def presets():
    ps=profiles()
    c=DoubleCoverConnection(beam=ps['W 360 x 39,0'],support=ps['HP 250 x 62,0 (H)'])
    from dataclasses import replace
    return {'W360 → HP250 · tração':c,'W360 → HP250 · compressão':replace(c,N=-2000,project='Duas talas — compressão de 2 kN'),
            'Geometria inicial da planilha · revisar':replace(c,beam=ps['W 150 x 13,0'],n=2,pitch=37.3333333333333,edge_v=37.3333333333333,edge_x=40,db=15.875,fin_t=4.3,root_height=148,stiffener_t=6.35,weld_web=3,weld_fin_stiffener=3,V=45000,N=70000,project='Planilha recebida — geometria inicial',notes='Perfis e esforços da planilha. Talas e soldas complementadas para representar a descrição; não é reprodução integral da planilha.')}


def compression_capacity(h,t,fy,length,k=1.):
    """Barra chata isolada, Q=1, sem ganho de seção composta: NBR 5.3/6.5.4."""
    if min(h,t,fy,length,k)<=0:raise ValueError('Dimensões de compressão inválidas.')
    area=h*t;r=t/math.sqrt(12);slender=k*length/r
    ne=math.pi**2*E*(h*t**3/12)/(k*length)**2
    lam0=math.sqrt(area*fy/ne)
    # Aplicar a curva de instabilidade também às barras curtas evita depender
    # do sinal inconsistente de L/r no exemplar fornecido do item 6.5.4-b.
    chi=.658**(lam0**2) if lam0<=1.5 else .877/lam0**2
    return chi*area*fy/G1,dict(slender=slender,chi=chi,ne=ne,lambda0=lam0,k=k,length=length)


def shim_factor(total):
    if total<0 or total>19:raise ValueError('Calços fora do intervalo de 0 a 19 mm.')
    return 1. if total<=6.3 else 1-.0154*(total-6.3)


def support_actions(c,V,N):
    M=V*c.pin_x
    top=N/2+M/c.root_height;bottom=N/2-M/c.root_height
    return dict(V=V,N=N,M=M,top=top,bottom=bottom)


def geometry(c):
    issues=[]
    def add(sev,text,ref='Geometria e modelo'):issues.append(Issue(sev,text,ref))
    fields=('db','pitch','edge_v','edge_x','gap','extension','fin_t','cover_t','stiffener_t','root_height','corner_clip','weld_web','weld_fin_stiffener','weld_stiffener_column','fw','clearance','tool_radius','fit_tolerance','V','N')
    if not all(type(getattr(c,k)) in (int,float) and math.isfinite(getattr(c,k)) for k in fields):
        add('error','Todas as entradas numéricas devem ser finitas.');return issues,{}
    if type(c.n) is not int or not 2<=c.n<=12 or any(type(getattr(c,k)) is not bool for k in ('threads','drilled','norm_minimum')):
        add('error','Número de linhas ou opções booleanas inválidos.');return issues,{}
    if c.shim_mode not in ('automatic','fit') or not any(abs(c.db-d)<1e-8 for d in DIAMETERS.values()) or c.bolt not in BOLTS:
        add('error','Parafuso ou modo de montagem não reconhecido.');return issues,{}
    if min(getattr(c,k) for k in fields if k not in ('V','N','corner_clip','clearance','fit_tolerance'))<=0 or min(c.corner_clip,c.clearance,c.fit_tolerance)<0:
        add('error','Dimensões positivas são obrigatórias; alívios e tolerâncias não podem ser negativos.');return issues,{}
    if c.fit_tolerance>1.:add('error','A tolerância adotada sem calços está limitada a 1 mm nesta versão; não é uma dispensa normativa.')
    for name,p,steel in [('Viga',c.beam,c.beam_steel),('Coluna',c.support,c.support_steel)]:
        vals=(p.d,p.bf,p.tw,p.tf,p.clear,p.area,p.mass)
        if not all(type(v) in (int,float) and math.isfinite(v) and v>0 for v in vals) or p.d<=2*p.tf or p.clear>p.d-2*p.tf or p.bf<=p.tw:
            add('error',name+': seção I inconsistente.');return issues,{}
    for name,steel,thick,plate in [('Viga',c.beam_steel,[c.beam.tw,c.beam.tf],c.beam.family in ('VS','CVS','CS','Soldado')),('Coluna',c.support_steel,[c.support.tw,c.support.tf],c.support.family in ('VS','CVS','CS','Soldado')),('Nervura',c.fin_steel,[c.fin_t],True),('Talas',c.cover_steel,[c.cover_t],True),('Enrijecedores',c.stiffener_steel,[c.stiffener_t],True)]:
        if steel not in STEELS:add('error',name+': aço desconhecido.');continue
        s=STEELS[steel];lo=s.plate_min if plate else s.profile_min;hi=s.plate_max if plate else s.profile_max
        if (plate and not s.plate_allowed) or (not plate and not s.rolled_allowed) or min(thick)<lo or max(thick)>hi:add('error',name+': aço/produto/espessura fora do intervalo cadastrado.',s.source)
    pmin=max(2.7*c.db,c.dh+c.db);pmax=min(24*min(c.fin_t,c.cover_t,c.beam.tw),300)
    if not pmin<=c.pitch<=pmax:add('error',f'Passo p deve estar entre {pmin:.2f} e {pmax:.2f} mm.',NBR+', 6.3.9/6.3.10')
    emin={12.7:19,15.875:22,19.05:25,22.225:28,25.4:32,28.575:38,31.75:41}[c.db]
    for name,e,t in [('vertical das talas/nervura',c.edge_v,min(c.cover_t,c.fin_t)),('horizontal da emenda',c.edge_x,min(c.cover_t,c.fin_t,c.beam.tw))]:
        if e<max(emin,c.dh/2):add('error',f'Borda {name} inferior a {emin} mm.',NBR+', tabela 16')
        if e>min(12*t,150):add('error',f'Borda {name} excede min(12t;150 mm).',NBR+', 6.3.12')
    if c.hp>=c.beam.clear-2*c.clearance:add('interference','Talas invadem mesas/concordâncias da viga; reduza altura ou aumente o perfil.')
    if (c.beam.clear-(c.n-1)*c.pitch)/2<c.tool_radius:add('interference','Porca/ferramenta interfere na concordância da viga.')
    if c.extension<2*c.edge_x+c.clearance:add('interference','A tala invade a coluna: adote u ≥ 2e + folga de montagem.')
    if c.extension-c.edge_x<c.tool_radius+c.weld_stiffener_column:add('interference','Grupo na nervura sem acesso para porca/ferramenta junto à mesa da coluna.')
    if c.root_height<c.hp+2*(c.clearance+c.weld_fin_stiffener):add('interference','Distância entre horizontais insuficiente para a tala e as soldas.')
    radius=(c.support.d-2*c.support.tf-c.support.clear)/2
    if c.corner_clip<radius:add('interference',f'Alívio de canto menor que a concordância estimada da coluna ({radius:.2f} mm).')
    if c.corner_clip>=min(c.projection,c.stiffener_span/2)/2:add('error','Alívio de canto elimina parcela excessiva do enrijecedor.')
    if (c.n-1)*c.pitch+c.dh_net>=c.beam.d:add('error','Um furo ultrapassa a seção da viga; ligamento resistente inválido.')
    if c.hp-c.n*c.dh_net<=0:add('error','Os furos eliminam a seção líquida das talas/nervura.')
    if c.shim_mode=='fit' and c.thickness_difference>c.fit_tolerance:add('error','Diferença de espessuras excede a tolerância de montagem adotada; utilize calços simétricos.')
    if c.shim_mode=='automatic' and c.thickness_difference>19:add('error','Soma dos calços excede 19 mm; revise espessuras ou use detalhamento específico.',NBR+', 6.5.7.2')
    if c.thickness_difference>0:
        if c.shim_mode=='automatic':add('info',f'Prever dois calços de {c.shim_each:.3f} mm no lado da {c.shim_side}, cobrindo a região parafusada. Não somar a espessura à resistência da peça central.',NBR+', 6.5.7.2')
        else:add('info',f'Diferença de {c.thickness_difference:.3f} mm dentro da tolerância de detalhamento adotada ({c.fit_tolerance:g} mm). Garantir contato firme e montagem simétrica; não é tolerância normativa.',NBR+', 6.3.1')
    welded=[('nervura–alma da coluna',c.weld_web,c.fin_t,c.support.tw,c.root_height-2*c.corner_clip),('nervura–horizontal',c.weld_fin_stiffener,c.fin_t,c.stiffener_t,c.projection-2*c.corner_clip),('horizontal–coluna',c.weld_stiffener_column,c.stiffener_t,min(c.support.tf,c.support.tw),c.projection-2*c.corner_clip)]
    for name,w,t,ts,length in welded:
        thin=min(t,ts);wmin=3 if thin<=6.3 else 5 if thin<=12.5 else 6 if thin<=19 else 8
        wmax=t if t<6.3 else t-1.5
        if w<wmin or w>wmax+1e-8:add('error',f'Filete {name}: usar entre {wmin:g} e {wmax:.2f} mm; espessura/execução deve ser compatível.',NBR+', 6.2.6.2')
        if length<max(4*w,40):add('error',f'Comprimento útil da solda {name} inferior a max(4w;40 mm).',NBR+', 6.2.6.2.3')
    if c.bolt=='ASTM A307':add('error','Nesta ligação, utilizar A325 ou A490; parafusos comuns A307 não estão implementados.')
    if c.hp<.5*c.beam.d:add('pending','Altura conectada menor que metade da viga: detalhamento fora do domínio adotado para a rótula.')
    if min(c.fin_t,c.beam.tw)>c.db/2+1.6 or c.cover_t>c.db/2+1.6:add('pending','Espessuras fora do limite geométrico conservador de flexibilidade; avaliar rotação da emenda.','Complemento AISC, Parte 10; limite de implementação')
    if not c.norm_minimum:add('pending','Mínimo normativo de 45 kN desativado: modo de comparação.',NBR+', 6.1.5.2')
    if c.V==0 and c.N==0:add('pending','Informe esforços não nulos; a direção do mínimo de 45 kN não está definida.')
    add('excluded',ASSEMBLY_NOTE,'Premissas adotadas e abrangência do modelo')
    add('info','Quatro horizontais: dois níveis, com uma chapa de cada lado da alma da coluna. A dupla oposta não aumenta automaticamente as resistências calculadas.','Modelo do detalhe')
    return issues,dict(hp=c.hp,cover_length=c.cover_length,fin_length=c.fin_length,pin_x=c.pin_x,group_e=c.group_e,shim_each=c.shim_each)


def strength(c,V,N,case):
    rows=[]
    def add(id,name,sd,rd,unit,ref,eq,sub,variables):rows.append(Check(id,name,sd,rd,unit,ref,eq,sub,variables,case))
    M=abs(V)*c.group_e
    forces=elastic_group(c.n,c.pitch,1,0,V,N,M)
    F=max(math.hypot(x,y) for x,y in forces);Dn=sum(abs(x) for x,y in forces);Dv=sum(abs(y) for x,y in forces)
    nominal=bolt_shear(c.db,BOLTS[c.bolt],c.threads or c.bolt=='ASTM A307')
    for side,central in [('fin',c.fin_t),('beam',c.beam.tw)]:
        shims=c.thickness_difference if c.shim_mode=='automatic' and central<max(c.fin_t,c.beam.tw) else 0.
        grip=central+2*c.cover_t+shims;kg=grip_factor(grip,c.db);ks=shim_factor(shims)
        add('dc_bolt_'+side,'Parafusos — '+('nervura' if side=='fin' else 'viga')+' / corte duplo',F,2*nominal*kg*ks,'N',NBR+', 6.3.3.2, 6.3.7, 6.5.7.2','FRd = 2·kpega·kcalço·α·Ab·fub/γa2',f'FSd={F:.3f}; Mgrupo={M:.3f}; pega={grip:.3f}; kpega={kg:.5f}; kcalço={ks:.5f}', 'Dois planos de corte por parafuso; os dois grupos transmitem o esforço integral. N axial provoca corte, não tração no eixo dos parafusos.')
    lc=min(c.edge_x-c.dh/2,c.edge_v-c.dh/2,c.pitch-c.dh)
    for id,label,t,steel,count in [('fin','Nervura',c.fin_t,c.fin_steel,1),('beam','Alma da viga',c.beam.tw,c.beam_steel,1),('cover','Duas talas',c.cover_t,c.cover_steel,2)]:
        s=STEELS[steel]
        shimmed=c.shim_mode=='automatic' and (id=='cover' or (id=='fin' and c.fin_t<c.beam.tw) or (id=='beam' and c.beam.tw<c.fin_t))
        ks=shim_factor(c.thickness_difference) if shimmed else 1.
        cap=ks*count*min(1.2*lc*t*s.fu,2.4*c.db*t*s.fu)/G2
        add('dc_bearing_'+id,label+' — contato e rasgamento',F,cap,'N',NBR+', 6.3.3.3/6.5.7.2','FRd = kcalço·nt·min(1,2lc t fu;2,4db t fu)/γa2',f'lc={lc:.4f}; t={t:.4f}; nt={count}; kcalço={ks:.5f}; Fmax={F:.3f}', 'Ligamento livre mínimo em qualquer direção. Cada tala recebe metade da força; calços sem crédito resistente. Para as talas, governa o grupo com maior enchimento.')
        le=c.edge_x;lv=c.edge_v+(c.n-1)*c.pitch;dn=c.dh_net;ell=(c.n-1)*c.pitch
        def block(Agv,Anv,Ant):return count*min(.6*s.fu*Anv+.5*s.fu*Ant,.6*s.fy*Agv+.5*s.fu*Ant)/G2
        rn=block(2*le*t,2*(le-dn/2)*t,(ell-(c.n-1)*dn)*t)
        rv=block(lv*t,(lv-(c.n-.5)*dn)*t,(le-dn/2)*t)
        add('dc_block_'+id,label+' — bloco e esforços do grupo',Dn/rn+Dv/rv,1,'—',NBR+', 6.5.6; combinação linear conservadora','η = Σ|Fx,i|/RN,bloco + Σ|Fy,i|/RV,bloco ≤ 1',f'Σ|Fx|={Dn:.3f}; Σ|Fy|={Dv:.3f}; RN={rn:.3f}; RV={rv:.3f}', 'Caminho U para componente axial e L para vertical; Cts=0,5. Envoltória dos módulos das forças individuais inclui momento e reversão. As duas extremidades iguais das talas são abrangidas.')

    def section(id,label,h,t,steel,Ns,Vs,Ms,L,holes=0,pair=1,k=1,splice=False):
        s=STEELS[steel];A=pair*h*t;An=pair*(h-holes*c.dh_net)*t;Ae=min(An,.85*A) if splice else An
        W=pair*t*h*h/6
        # Momento de inércia líquido de furos retangulares centrados, conservador.
        I=t*h**3/12
        if holes:
            for i in range(holes):
                y=(i-(holes-1)/2)*c.pitch
                I-=t*(c.dh_net**3/12+c.dh_net*y*y)
        Wn=pair*I/(h/2)
        if min(An,Ae,Wn)<=0:raise ValueError('Seção líquida não positiva.')
        sigma=abs(Ns)/A+abs(Ms)/W;tau=1.5*abs(Vs)/A
        add('dc_yield_'+id,label+' — tensões combinadas',math.hypot(sigma,math.sqrt(3)*tau),s.fy/G1,'MPa',NBR+', 6.5; critério elástico de von Mises','σeq = √[(|N|/Ag+|M|/Wg)²+3(1,5|V|/Ag)²]',f'Ag={A:.3f}; Wg={W:.3f}; N={Ns:.3f}; V={Vs:.3f}; M={Ms:.3f}; σeq={math.hypot(sigma,math.sqrt(3)*tau):.5f}', 'Limite elástico conservador; sem redistribuição plástica. h e t são a faixa resistente declarada, não a seção global da viga.')
        tension=max(0,Ns/Ae+abs(Ms)/Wn)
        eta=tension/(s.fu/G2)+abs(Vs)/(.6*s.fu*An/G2)
        add('dc_net_'+id,label+' — seção líquida',eta,1,'—',NBR+', 6.5.3/6.5.5; envoltória linear','η = max(0;N/Ae+|M|/Wn)/(fu/γa2) + |V|/(0,6fu An/γa2)',f'An={An:.3f}; Ae={Ae:.3f}; Wn={Wn:.3f}; η={eta:.5f}', 'Ae=min(An;0,85Ag) nas talas de emenda; demais faixas Ae=An. Compressão não é transformada em tração. Furos deduzidos sem reutilizar área de calços.')
        nr,props=compression_capacity(h,t,s.fy,L,k);nr*=pair
        mr,_=plate_ltb(h,t,L,s.fy,Cb=1.);mr=pair*mr/G1
        vr=pair*min(.6*s.fy*h*t/G1,.6*s.fu*(h-holes*c.dh_net)*t/G2)
        # Barra chata isolada e LTB sem crédito de solidarização entre talas.
        nrd=nr if Ns<0 else min(s.fy*A/G1,s.fu*Ae/G2)
        eta=abs(Ns)/nrd+abs(Ms)/mr+abs(Vs)/vr
        add('dc_stability_'+id,label+' — estabilidade e interação',eta,1,'—',NBR+', 5.3/6.5.4; AISC F11; interação linear declarada','η = |N|/NRd + |M|/MRd + |V|/VRd ≤ 1',f'L={L:.3f}; K={k:g}; KL/r={props["slender"]:.3f}; χ={props["chi"]:.5f}; NRd={nrd:.3f}; MRd={mr:.3f}; VRd={vr:.3f}', 'Compressão: χAgfy/γa1; K e L explícitos. Flexão: barra chata AISC F11, Cb=1. Cada tala é isolada para instabilidade. Modelo de componente, não estabilidade acoplada do nó.')
    section('cover','Duas talas',c.hp,c.cover_t,c.cover_steel,N,V,M,2*c.group_e,c.n,2,1,True)
    section('fin','Nervura — aba livre',c.hp,c.fin_t,c.fin_steel,N,V,abs(V)*(c.extension+c.gap/2),c.extension+c.gap/2,c.n,1,2)
    section('root','Nervura — trecho interno',c.root_height,c.fin_t,c.fin_steel,N,V,abs(V)*c.pin_x,c.pin_x,0,1,2)
    section('beam','Alma da viga — faixa conectada',c.hp,c.beam.tw,c.beam_steel,N,V,M,c.group_e,c.n,1,2)
    action=support_actions(c,V,N);H=max(abs(action['top']),abs(action['bottom']))
    sl=c.stiffener_span;b=c.stiffener_width-2*c.corner_clip;ts=c.stiffener_t;s=STEELS[c.stiffener_steel]
    # Faixa horizontal como viga simplesmente apoiada entre mesas, H central no plano.
    mh=H*sl/4;mr,_=plate_ltb(b,ts,sl,s.fy,Cb=1.);mr/=G1
    vr=min(.6*s.fy*b*ts/G1,.6*s.fu*b*ts/G2)
    eta=mh/mr+(H/2)/vr
    add('dc_stiffener','Horizontais frontais — flexão/corte',eta,1,'—','Modelo de faixa biapoiada; '+NBR+', 6.5; AISC F11','η = (|H|s/4)/MRd + (|H|/2)/VRd',f'Hsup={action["top"]:.3f}; Hinf={action["bottom"]:.3f}; Hmax={H:.3f}; b útil={b:.3f}; s={sl:.3f}; M={mh:.3f}; MRd={mr:.3f}; VRd={vr:.3f}', 'Carga H no plano da chapa horizontal; W=t·b²/6. Sem crédito da solda à alma na flexão da faixa. Duas chapas frontais calculadas pela maior força; par oposto sem soma automática. Não verifica sua função de contenção do nó.')
    def weld(id,label,force,w,length,base_t,base_steel,other_t,other_steel):
        capacity=2*(w/math.sqrt(2))*length*.6*c.fw/G2
        add('dc_weld_'+id,label+' — solda',force,capacity,'N',NBR+', 6.2.5','FRd = 2(w/√2)L·0,6fw/γw2',f'FSd={force:.3f}; w={w:.3f}; L útil={length:.3f}; fw={c.fw:g}', 'Dois filetes contínuos; sem aumento direcional. Solda chapa–apoio ou chapa–chapa; não há solda direta viga–coluna.')
        fy=STEELS[base_steel].fy;fu=STEELS[base_steel].fu;fy2=STEELS[other_steel].fy;fu2=STEELS[other_steel].fu
        cap=length*min(.6*fy*base_t/G1,.6*fu*base_t/G2,.6*fy2*other_t/G1,.6*fu2*other_t/G2)
        add('dc_base_'+id,label+' — metal-base',force,cap,'N',NBR+', 6.5.5','FRd = L·min(0,6fy t/γa1;0,6fu t/γa2), ambas as peças',f't1={base_t:.4f}; t2={other_t:.4f}; L={length:.3f}; FRd={cap:.3f}', 'Resultante limitada conservadoramente pela resistência ao corte do metal-base; não duplica a espessura da peça pela existência de dois filetes.')
    weld('web','Nervura–alma da coluna',abs(V),c.weld_web,c.root_height-2*c.corner_clip,c.fin_t,c.fin_steel,c.support.tw,c.support_steel)
    weld('fin_h','Nervura–horizontal',H,c.weld_fin_stiffener,b,c.fin_t,c.fin_steel,ts,c.stiffener_steel)
    weld('h_flange','Horizontal–mesa da coluna',H/2,c.weld_stiffener_column,b,ts,c.stiffener_steel,c.support.tf,c.support_steel)
    # Envoltória adicional: a solda à alma é conferida para H integral, sem ganho nas demais.
    weld('h_web','Horizontal–alma da coluna',H,c.weld_stiffener_column,sl-2*c.corner_clip,ts,c.stiffener_steel,c.support.tw,c.support_steel)
    sy=STEELS[c.support_steel]
    add('dc_col_web','Coluna — corte local junto à nervura',abs(V),min(.6*sy.fy*2*c.root_height*c.support.tw/G1,.6*sy.fu*2*c.root_height*c.support.tw/G2),'N',NBR+', 6.5.5','VRd = 2Htw·min(0,6fy/γa1;0,6fu/γa2)',f'H={c.root_height:g}; tw={c.support.tw:g}; V={abs(V):.3f}', 'Verificação local. Esforços globais da coluna e das demais barras do nó não são entradas deste módulo.')
    return rows,action


def evaluate(c):
    issues,g=geometry(c)
    if any(i.severity=='interference' for i in issues):issues.append(Issue('excluded',INTERFERENCE_ASSUMPTION))
    r=Result(issues=issues,geometry=g)
    if any(x.severity=='error' for x in issues):return r
    if c.V==0 and c.N==0:return r
    r.actual,actual_actions=strength(c,c.V,c.N,'Entrada')
    r.minimum_factor=max(1,45000/math.hypot(c.V,c.N)) if c.norm_minimum else 1
    if r.minimum_factor>1:
        r.checks,actions=strength(c,c.V*r.minimum_factor,c.N*r.minimum_factor,'Mínimo de 45 kN')
    else:r.checks=list(r.actual);actions=actual_actions
    r.geometry.update(actions=actions,actual_actions=actual_actions)
    return r
