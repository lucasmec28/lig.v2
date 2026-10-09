"""End plates na mesa de coluna. N, mm, MPa; ações já de cálculo.

Resistências NBR 8800:2024/2025. Linhas de plastificação e critério
construtivo FR complementares do DG39 (2023), caso 4E não enrijecido.
Não se extrapolam os intervalos ensaiados nem se converte uma tabela LRFD.
"""
from dataclasses import dataclass, asdict, fields
import math
from .models import Profile, Check, Issue, Result, STEELS, BOLTS, DIAMETERS, VERSION, profiles
from .engine import bolt_shear
from .local_checks import grip_factor, web_shear
from .column_checks import crippling_point

G1=1.10;G2=1.35;E=200000.
NBR='ABNT NBR 8800:2024, versão corrigida 2025'
DG='AISC Design Guide 39 (2023)'
SCI='SCI P358 (2014), 4.7, Check 1'
STOCK={'1/4"':6.35,'5/16"':7.9375,'3/8"':9.525,'1/2"':12.7,'5/8"':15.875,'3/4"':19.05,'7/8"':22.225,'1"':25.4,'1 1/4"':31.75,'1 1/2"':38.1}

@dataclass(frozen=True)
class EndPlate:
    beam: Profile
    support: Profile
    kind: str='pinned'
    layout: str='both'
    project: str='End plate na mesa de coluna'
    beam_steel: str='ASTM A572 Gr.50'
    support_steel: str='ASTM A36'
    plate_steel: str='ASTM A36'
    bolt: str='ASTM F3125 A325'
    db: float=19.05
    tp: float=9.525
    bp: float=180.
    gauge: float=100.
    n: int=4
    pitch: float=70.
    overhang: float=5.
    pfi: float=45.
    pfo: float=40.
    edge: float=35.
    weld: float=5.
    fw: float=485.
    reinforced_edge: bool=True
    threads: bool=True
    drilled: bool=False
    norm_minimum: bool=True
    tool_radius: float=18.
    V: float=11000.
    N: float=2000.
    M: float=0.
    notes: str=''
    @property
    def dh(self):return self.db+(1.5875 if self.db<25.4 else 3.175)
    @property
    def dn(self):return self.dh+(0 if self.drilled else 2.)
    @property
    def ext_top(self):return self.overhang if self.kind=='pinned' else self.pfo+self.edge
    @property
    def ext_bottom(self):return self.overhang if self.kind=='pinned' or self.layout=='top' else self.pfo+self.edge
    @property
    def hp(self):return self.beam.d+self.ext_top+self.ext_bottom
    @property
    def rows(self):
        # y é positivo para baixo a partir da face superior da viga.
        if self.kind=='pinned':return [(self.beam.d-(self.n-1)*self.pitch)/2+i*self.pitch for i in range(self.n)]
        return [-self.pfo,self.beam.tf+self.pfi,self.beam.d-self.beam.tf-self.pfi]+([self.beam.d+self.pfo] if self.layout=='both' else [])
    @property
    def count(self):return 2*len(self.rows)
    @property
    def assumptions(self):
        common=[
            'Análise local em duas dimensões. Esforços de cálculo no nó, no plano da alma da viga; N positivo é tração. V é vertical. Não há momento no eixo de menor inércia nem cortante horizontal.',
            'Uma viga ortogonal e centrada na alma da coluna; coluna contínua, sem extremidade, emenda ou abertura próxima ao grupo. Não há viga oposta ou outras cargas locais concorrentes no nó.',
            'Viga com contenção eficaz; impedido o deslocamento lateral relativo das mesas da coluna. Juntas internas mesa–alma dos perfis soldados com penetração total e metal de adição compatível.',
            'Chapa e coluna pintadas ou protegidas contra corrosão. Espaçamentos máximos avaliados na região em contato; os prolongamentos da coluna contínua além do contorno da chapa não são bordas de uma emenda sobreposta.',
            'Furos padrão, ligação por contato, parafusos de alta resistência com protensão inicial conforme NBR 6.8, sem crédito ao atrito. Chapa e mesa da coluna em contato, sem calços. Soldagem em oficina.',
            'Análise global da coluna, interação com seu esforço axial, efeitos de segunda ordem e compatibilidade com a estrutura são externos ao modelo local. Não se avaliam fadiga, vibração, ações cíclicas, sismo ou incêndio.',
            'Dimensões de ferramenta são envelopes de montagem informados; comprimentos de parafusos, arruelas, preparação das juntas e tolerâncias devem constar do detalhamento de fabricação.',
        ]
        if self.kind=='pinned':common += [
            'Rotulada de altura total: parafusos somente entre mesas, chapa fina e gabarito de 90 a 140 mm. SCI P358 é usado como referência de detalhamento; resistências e interação N/V seguem NBR. Aço da chapa limitado a fy ≤ 275 MPa nesta configuração.',
            'A tração é atribuída conservadoramente à alma, sem crédito às soldas das mesas; distribuição igual por parafuso. A compressão é transmitida por contato. O modelo não recebe momento externo.',
            'Para não desprezar alavanca indevidamente, exige-se chapa e mesa da coluna rígidas sob a tração calculada, pela NBR 6.3.5.3. Essa condição local de alavanca nula não é classificação de rigidez rotacional do nó.',
            'Filetes contínuos na alma e nas mesas da viga; borda reforçada admitida onde explicitamente indicada.' if self.reinforced_edge else 'Filetes contínuos na alma e nas mesas da viga, sem reforço de borda.',
        ]
        else:common += [
            'End plate estendida sem nervuras, configuração 4E do DG39: duas linhas tracionadas, dois parafusos por linha. A rigidez é adotada pelo procedimento construtivo FR do guia, dentro do domínio ensaiado; adota-se a simplificação da NBR 6.1.2.3, a critério do responsável técnico. Não é calculada uma curva momento–rotação nem se verifica Si ≥ 25EI/L ou Kv/Kp da análise global.',
            'Método de chapa espessa: chapa e mesa da coluna devem resistir a 1,10 Meq antes da plastificação; γr=1,0. Resistências nominais do mecanismo são divididas por γa1. A versão também exige espessura não menor que a obtida com φb=0,90 do guia.',
            'N é distribuído igualmente entre as mesas. Para tração, Meq=|M|+N(d−tf)/2. Não se usa o alívio de tração causado por compressão. Domínio limitado a |N|(d−tf)/2 ≤ |M|/2.',
            'As soldas das duas mesas e da alma da viga à chapa de topo são de penetração total, com metal de adição compatível. Esta especificação é própria da end plate engastada; não cria solda entre viga e coluna.',
            'A verificação do painel da coluna usa somente a contribuição da alma, sem ganho das mesas. Adota-se Ncol,Sd ≤ 0,4 Ag,col fy,col e despreza-se o cortante favorável da coluna. Outros esforços de nó exigem compatibilização externa.',
        ]
        return common
    def to_dict(self):return {'schema_version':1,'app_version':VERSION,'connection_type':'end_plate','connection':asdict(self),'fixed_assumptions':self.assumptions}
    @staticmethod
    def from_dict(data):
        if not isinstance(data,dict) or data.get('connection_type')!='end_plate' or data.get('schema_version')!=1:raise ValueError('Selecione um projeto de end plate desta versão.')
        d=dict(data['connection']);d['beam']=Profile(**d['beam']);d['support']=Profile(**d['support']);return EndPlate(**d)


def yield_4e(bp,g,h1,h2,pfo,pfi):
    """DG39 Tabela 5-10. Todas as medidas na mesma unidade; Y tem dimensão L."""
    s=math.sqrt(bp*g)/2;pi=min(pfi,s)
    return bp/2*(h1/pfo+h2*(1/pi+1/s)-.5)+2/g*h2*(s+pi)


def yield_column_4e(bfc,g,h1,h2,c):
    """DG39 eq. 3-44, coluna contínua não enrijecida."""
    s=math.sqrt(bfc*g)/2
    return bfc/2*(h1+h2)/s+2/g*(h2*(3*c/4+s)+h1*(c/4+s)+c*c/2)+g/2


def thick_required(M,fy,Y,gamma=G1):return math.sqrt(1.10*M*max(gamma,1/.90)/(fy*Y))


def rigid_strip(T,b,p,fu,db):
    """NBR 6.3.5.3. b é distância do eixo do furo à face do elemento tracionado."""
    return math.sqrt(4*max(b-db/2,0)*T*G1/(p*fu))


def tributaries(rows,lo,hi,b):
    # NBR 6.3.5.2, faixas externas/internas; espaçamentos não uniformes
    # recebem metade do intervalo em cada lado, limitada a 1,75b.
    return [min(y-lo if i==0 else (y-rows[i-1])/2,1.75*b)+min(hi-y if i==len(rows)-1 else (rows[i+1]-y)/2,1.75*b) for i,y in enumerate(rows)]


def validate(c):
    out=[]
    def err(t,ref='Geometria e domínio do modelo'):out.append(Issue('error',t,ref))
    nums=[f.name for f in fields(c) if isinstance(getattr(c,f.name),(int,float)) and not isinstance(getattr(c,f.name),bool)]
    if any(not math.isfinite(getattr(c,k)) for k in nums):err('Todos os números devem ser finitos.');return out
    if any(getattr(c,k)<=0 for k in ('db','tp','bp','gauge','pitch','overhang','pfi','pfo','edge','weld','fw','tool_radius')):err('Dimensões e resistências devem ser positivas.');return out
    if c.kind not in ('pinned','moment') or c.layout not in ('top','both'):err('Tipo ou extensão de chapa inválido.');return out
    if isinstance(c.n,bool) or not isinstance(c.n,int) or not 2<=c.n<=10:err('Usar de 2 a 10 linhas inteiras.');return out
    if c.bolt not in BOLTS or c.bolt=='ASTM A307' or not any(abs(c.db-v)<1e-6 for v in DIAMETERS.values()):err('Usar parafuso A325/A490 e diâmetro imperial disponível.');return out
    if any(not isinstance(getattr(c,k),bool) for k in ('threads','drilled','norm_minimum','reinforced_edge')):err('Opção booleana inválida.');return out
    for p,name,steel in [(c.beam,'viga',c.beam_steel),(c.support,'coluna',c.support_steel)]:
        if steel not in STEELS:err('Aço da '+name+' não reconhecido.');continue
        if any(not math.isfinite(getattr(p,k)) or getattr(p,k)<=0 for k in ('d','bf','tw','tf','clear','area')) or p.d<=2*p.tf or p.bf<=p.tw or p.clear>p.d-2*p.tf+1:err('Seção da '+name+' inválida.');continue
        st=STEELS[steel];welded=p.family in ('CS','CVS','VS','Soldado')
        if (welded and not st.plate_allowed) or (not welded and not st.rolled_allowed) or min(p.tf,p.tw)<st.profile_min or max(p.tf,p.tw)>st.profile_max:err('Material incompatível com produto/espessura da '+name+'.')
    if c.plate_steel not in STEELS:err('Aço da chapa não reconhecido.');return out
    sp=STEELS[c.plate_steel]
    if not sp.plate_allowed or not sp.plate_min<=c.tp<=sp.plate_max:err('Aço da chapa incompatível com a espessura/produto.');return out
    if out:return out
    b,s=c.beam,c.support;rows=c.rows
    edge_min={12.7:19,15.875:22,19.05:25,22.225:28,25.4:32,28.575:38,31.75:41}[c.db]
    if c.bp>min(s.bf,b.bf+max(25.4,c.tp))+1e-6 and c.kind=='moment':err('Largura efetiva da end plate deve caber na coluna e ser ≤ bf da viga + max(25,4 mm; tp).',DG+', 3.4')
    if c.bp>s.bf:err('A chapa ultrapassa a largura da mesa da coluna.')
    if c.bp<b.bf+2*c.weld and c.kind=='pinned':err('A largura da chapa não deixa espaço lateral para os filetes das mesas.')
    if (min(c.bp,s.bf)-c.gauge)/2<max(edge_min,c.tool_radius):err('Borda lateral insuficiente para o furo ou a ferramenta.')
    root_b=(b.d-b.clear)/2;root_c=(s.d-s.clear)/2-s.tf
    if c.gauge/2<=max(b.tw/2+c.weld,s.tw/2+max(root_c,0))+c.tool_radius:err('O gabarito dos parafusos interfere com a alma, concordância ou solda.')
    if any(y2-y1<8*c.db/3 for y1,y2 in zip(rows,rows[1:])):err('Passo entre linhas inferior a 8db/3.',NBR+', 6.3.7')
    if c.gauge<8*c.db/3:err('Gabarito horizontal inferior a 8db/3.',NBR+', 6.3.7')
    pmax=min(24*min(c.tp,s.tf),300.)
    if max([c.gauge]+[y2-y1 for y1,y2 in zip(rows,rows[1:])])>pmax:
        err(f'Espaçamento máximo na região em contato: {pmax:g} mm. Rever passo, espessura ou arranjo de parafusos.',NBR+', 6.3.10(a)')
    if max((c.bp-c.gauge)/2,rows[0]+c.ext_top,b.d+c.ext_bottom-rows[-1])>min(12*c.tp,150.):
        err('Distância máxima à borda da chapa excede min(12tp;150 mm).',NBR+', 6.3.12')
    # Parafusos externos não podem interceptar a mesa; internos precisam deixar ferramenta.
    for y in rows:
        if 0<=y<=b.d and not root_b+c.weld+c.tool_radius<=y<=b.d-root_b-c.weld-c.tool_radius:err('Linha interna interfere com mesa, concordância, solda ou ferramenta.');break
        if y<0 and -y<c.tool_radius+c.weld:err('Linha superior externa muito próxima da mesa.');break
        if y>b.d and y-b.d<c.tool_radius+c.weld:err('Linha inferior externa muito próxima da mesa.');break
    if min(rows[0]+c.ext_top,b.d+c.ext_bottom-rows[-1])<max(edge_min,c.tool_radius):err('Distância do furo à borda superior/inferior insuficiente.')
    if c.kind=='pinned':
        if abs(c.M)>1e-9:err('Ligação rotulada recebe somente V e N; remova o momento externo.')
        if not 90<=c.gauge<=140:err('Para a rótula de altura total, usar gabarito entre 90 e 140 mm.',SCI)
        if sp.fy>275:err('A classificação rotulada deste modelo está limitada a chapa com fy ≤ 275 MPa; use A36.',SCI)
        if c.overhang<c.weld:err('A sobra superior/inferior deve acomodar o filete.')
        if c.overhang>10:err('A sobra da rotulada é limitada a 10 mm neste modelo; valor usual 5 mm.')
        if (c.n-1)*c.pitch<b.d/2:err('O grupo da rotulada deve abranger ao menos metade da altura da viga.')
        tmax=min(b.tw,b.tf,c.tp) if c.reinforced_edge else min(b.tw,b.tf,c.tp)-1.5
        if c.weld>tmax+1e-9:err('Filete excede a borda disponível; revise espessura ou preparação.')
        thick=max(b.tf,c.tp);wmin=3 if thick<=6.35 else 5 if thick<=12.5 else 6 if thick<=19 else 8
        if c.weld<wmin:err(f'Filete mínimo: {wmin:g} mm.',NBR+', 6.2.4/tabela 8')
    else:
        if sp.fy>345:err('O domínio do DG39 adotado para a chapa é fy ≤ 345 MPa.',DG+', 3.4')
        if c.fw<max(STEELS[c.beam_steel].fu,sp.fu):err('A solda de penetração total exige metal de adição compatível com os metais-base.')
        if c.gauge>b.bf:err('No modelo 4E, o gabarito não deve exceder bf da viga.',DG)
        limits=[('pfi',c.pfi,25.4,63.5),('pfo',c.pfo,25.4,63.5),('extensão',c.ext_top,63.5,190.5),('gabarito',c.gauge,69.85,177.8),('altura da viga',b.d,400.05,1828.8),('largura da chapa',c.bp,127,260.35),('mesa da viga',b.tf,9.525,25.4)]
        for name,val,lo,hi in limits:
            if not .9*lo<=val<=1.1*hi:err(f'{name}: {val:g} mm fora do intervalo {lo*.9:g}–{hi*1.1:g} mm, com tolerância de 10%.',DG+', 5.3.1/tabela 5-9')
        if c.layout=='top' and c.M<=0:err('Extensão só acima: este modelo 4E exige M > 0 (tração na mesa superior). Para inversão, escolha extensão acima e abaixo.')
        if abs(c.M)<1e-6 or abs(c.N)*(b.d-b.tf)>abs(c.M):err('O modelo de engaste 4E exige momento dominante: |N|(d−tf) ≤ |M|. Para axial dominante, é necessário outro modelo de distribuição.',DG+', 3.5')
    if max(abs(c.V),abs(c.N),abs(c.M))==0:err('Informe pelo menos um esforço não nulo.')
    if not c.norm_minimum:out.append(Issue('pending','Conferência normativa mínima desativada: modo de comparação.',NBR+', 6.1.5'))
    return out


def _calculate(c,V,N,M,case):
    b,s=c.beam,c.support;sp=STEELS[c.plate_steel];sb=STEELS[c.beam_steel];sc=STEELS[c.support_steel]
    rows=[];a={};nb=c.count;fub=BOLTS[c.bolt];Ab=math.pi*c.db**2/4
    def add(i,name,sd,rd,unit,ref,eq,sub,var):rows.append(Check('ep_'+i,name,sd,rd,unit,ref,eq,sub,var,case))
    nbolts=len(c.rows);shear=abs(V)/nb
    Ft=.75*fub*Ab/G2;Fv=bolt_shear(c.db,fub,c.threads)*grip_factor(c.tp+s.tf,c.db)
    if c.kind=='moment':
        z=b.d-b.tf;Meq=abs(M)+max(N,0)*z/2;h1=b.d-b.tf/2+c.pfo;h2=b.d-1.5*b.tf-c.pfi
        # Equal tension in the two active rows, DG39 thick-plate force model.
        Tb=Meq/(2*(h1+h2));T=4*Tb;C=T-N
        Yp=yield_4e(c.bp,c.gauge,h1,h2,c.pfo,c.pfi)
        Yc=yield_column_4e(s.bf,c.gauge,h1,h2,c.pfo+b.tf+c.pfi)
        tp_req=thick_required(Meq,sp.fy,Yp);tc_req=thick_required(Meq,sc.fy,Yc)
        add('plate_rigidity','Chapa — espessura para chapa espessa e critério FR',tp_req,c.tp,'mm',DG+', 3.2, 5.1.1 eq.5-4 e tabela 5-10','tp,req = √[1,10 Meq max(γa1;1/0,90)/(fy Yp)]',f'Meq={Meq:.3f}; Yp={Yp:.6f}; fy={sp.fy:g}; tp,req={tp_req:.4f}', 'Meq: momento equivalente; Yp: parâmetro de linhas de plastificação; γr=1. Chapa espessa evita alavanca no domínio do guia.')
        add('column_rigidity','Coluna — espessura da mesa sem alavanca',tc_req,s.tf,'mm',DG+', 3.7.6 eq.3-44 e 5.1.1','tf,req = √[1,10 Meq max(γa1;1/0,90)/(fyc Yc)]',f'Yc={Yc:.6f}; fyc={sc.fy:g}; tf,req={tc_req:.4f}', 'Coluna contínua sem enrijecedores; parâmetro Yc com o mesmo grupo 4E. Não se ignora a deformação da mesa da coluna.')
        add('plate_yield','Chapa — linhas de plastificação',Meq,sp.fy*c.tp**2*Yp/G1,'Nmm',DG+', tabela 5-10; '+NBR+', γa1','MRd=fy tp² Yp/γa1',f'Yp={Yp:.6f}; tp={c.tp:g}; MRd={sp.fy*c.tp**2*Yp/G1:.3f}','Resistência nominal do mecanismo 4E; mínimo de chapa espessa verificado separadamente.')
        # Elastic end section for weld/base. No local beam holes in this connection.
        te=min(b.tf,c.tp);we=min(b.tw,c.tp);hw=b.d-2*b.tf
        A=2*b.bf*te+hw*we;I=2*(b.bf*te**3/12+b.bf*te*(b.d/2-b.tf/2)**2)+we*hw**3/12;W=I/(b.d/2)
        sigma=abs(N)/A+abs(M)/W;tau=abs(V)/(we*hw);equiv=math.hypot(sigma,math.sqrt(3)*tau)
        add('weld_cjp','Viga e juntas de penetração total — tensão equivalente',equiv,min(sb.fy,sp.fy)/G1,'MPa',NBR+', 6.2.5/tabela 9 e 6.5','σeq=√[(|N|/A+|M|/W)²+3(V/Aw)²]',f'A={A:.3f}; W={W:.3f}; Aw={we*hw:.3f}; σeq={equiv:.4f}', 'Critério elástico conservador, combinando máximos de tensões. Gargantas limitadas a min(tp;tf) nas mesas e min(tp;tw) na alma. Juntas CJP em ambas as mesas e alma, metal de adição compatível.')
        flange_lambda=(b.bf-b.tw)/(2*b.tf);web_lambda=b.clear/b.tw
        add('compact_flange','Viga — mesa compacta no nó',flange_lambda,.38*math.sqrt(E/sb.fy),'—',NBR+', 5.4 e anexo D','(bf−tw)/(2tf) ≤ 0,38√(E/fy)',f'λ={flange_lambda:.4f}; fy={sb.fy:g}', 'Restrição conservadora do modelo à seção compacta; não substitui o dimensionamento global da viga.')
        add('compact_web','Viga — alma compacta no nó',web_lambda,3.76*math.sqrt(E/sb.fy),'—',NBR+', 5.4 e anexo D','h/tw ≤ 3,76√(E/fy)',f'λ={web_lambda:.4f}; fy={sb.fy:g}', 'Limite conservador para a flexão; esforço axial dominante é excluído pelo domínio do DG39.')
        a.update(Meq=Meq,Yp=Yp,Yc=Yc,tp_required=tp_req,column_tf_required=tc_req,h1=h1,h2=h2,z=z)
    else:
        Tb=max(N,0)/nb;T=max(N,0);C=max(-N,0);z=b.d-b.tf
        # Uniform pure axial load, no external moment in a nominally pinned joint.
        for key,t,fu,tw,lo,hi,label in [('plate',c.tp,sp.fu,b.tw,-c.ext_top,b.d+c.ext_bottom,'Chapa'),('column',s.tf,sc.fu,s.tw,-c.ext_top,b.d+c.ext_bottom,'Mesa da coluna')]:
            arm=(c.gauge-tw)/2;ps=tributaries(c.rows,lo,hi,arm);pmin=min(ps)
            tr=rigid_strip(Tb,arm,pmin,fu,c.db)
            add(key+'_prying',label+' — espessura para alavanca nula',tr,t,'mm',NBR+', 6.3.5.2 e 6.3.5.3','tmin=√[4(b−db/2) Ft,0,Sd γa1/(p fu)]',f'b={arm:.4f}; p={pmin:.4f}; Ft,0,Sd={Tb:.3f}; fu={fu:g}; tmin={tr:.4f}', 'b: eixo do parafuso à face da alma; p: menor largura tributária limitada pela NBR. Usa-se o menor p para todas as linhas, sem alavanca omitida se o requisito falhar.')
            if key=='plate':a['tp_required']=tr
            else:a['column_tf_required']=tr
        limit=10. if b.d<=457 else 12.
        add('rotation','Rótula — limite construtivo de espessura',c.tp,limit,'mm',SCI,'tp ≤ 10 mm (d ≤ 457 mm); tp ≤ 12 mm (d > 457 mm)',f'tp={c.tp:g}; d={b.d:g}; limite={limit:g}', 'Limite conservador de detalhamento para chapa com fy ≤ 275 MPa. Não é resistência sob a carga nem mola rotacional calculada.')
        add('ductility','Rótula — ductilidade chapa e parafuso',c.tp,c.db/1.9*math.sqrt(fub/sp.fy),'mm',SCI+', nota 4','tp ≤ (db/1,9)√(fub/fy)',f'db={c.db:g}; fub={fub:g}; fy={sp.fy:g}', 'Condição de ductilidade, independente da verificação de resistência à tração de cálculo.')
        L=max(b.clear-2*c.weld,0);a_w=2*c.weld/math.sqrt(2)*L;load=math.hypot(V,N)
        add('weld_fillet','Soldas alma–chapa — resultante V e N',load,.6*c.fw*a_w/G2,'N',NBR+', 6.2.5','FRd=0,6 fw · 2(w/√2)L/γw2',f'L={L:.3f}; w={c.weld:g}; Aw={a_w:.3f}; R={load:.3f}', 'Dois filetes na alma, descontadas extremidades. Filetes nas mesas são exigidos no detalhe mas não recebem crédito na resistência à resultante.')
        Rbase=L*min(b.tw*sb.fy,c.tp*sp.fy)*.6/G1
        add('base_weld','Metal-base junto à solda da alma',load,Rbase,'N',NBR+', 6.5.5','FRd=0,6 L min(tw fyb;tp fyp)/γa1',f'L={L:.3f}; tw={b.tw:g}; tp={c.tp:g}; FRd={Rbase:.3f}', 'Verificação conservadora da resultante por resistência ao cisalhamento; uma faixa conectada da alma e uma da chapa.')
    a.update(V=V,N=N,M=M,bolt_tension=Tb,bolt_shear=shear,T=T,C=max(C,0))
    add('bolt_shear','Parafusos — cisalhamento',shear,Fv,'N',NBR+', 6.3.3.2','Fv,Rd=kpega α Ab fub/γa2',f'Ab={Ab:.4f}; α={.45 if c.threads else .56}; Fv,Sd={shear:.3f}; Fv,Rd={Fv:.3f}','Um plano de corte. α=0,45 com rosca; 0,56 sem rosca. V distribuído a todos os parafusos, inclusive aos tracionados.')
    add('bolt_tension','Parafusos — tração',Tb,Ft,'N',NBR+', 6.3.3.1','Ft,Rd=0,75 Ab fub/γa2',f'Ft,Sd={Tb:.3f}; Ft,Rd={Ft:.3f}','Força por parafuso sem alavanca; válida quando chapa e mesa da coluna atendem às espessuras requeridas.')
    eta=(Tb/Ft)**2+(shear/Fv)**2
    add('bolt_interaction','Parafusos — interação tração e cisalhamento',eta,1.,'—',NBR+', 6.3.3.4','η=(Ft,Sd/Ft,Rd)²+(Fv,Sd/Fv,Rd)² ≤ 1',f'η=({Tb:.3f}/{Ft:.3f})²+({shear:.3f}/{Fv:.3f})²={eta:.6f}','Combinação elíptica da NBR vigente. Não se soma N diretamente ao cisalhamento do parafuso.')
    ys=c.rows
    for key,t,fu,fy,width,edge_y,label in [('plate',c.tp,sp.fu,sp.fy,c.bp,min(ys[0]+c.ext_top,b.d+c.ext_bottom-ys[-1]),'Chapa'),('column',s.tf,sc.fu,sc.fy,s.bf,None,'Mesa da coluna')]:
        distances=[y2-y1-c.dh for y1,y2 in zip(ys,ys[1:])]
        if edge_y is not None:distances.append(edge_y-c.dh/2)
        lc=min(distances);Rb=min(1.2*lc*t*fu,2.4*c.db*t*fu)/G2
        add('bearing_'+key,label+' — contato nos furos',shear,Rb,'N',NBR+', 6.3.3.3','Fc,Rd=min(1,2 lc t fu;2,4 db t fu)/γa2',f'lc={lc:.4f}; t={t:g}; Fc,Rd={Rb:.3f}', 'Menor ligamento livre aplicado conservadoramente a todos os furos. Coluna contínua sem borda longitudinal próxima.')
        if key=='plate':
            # Both side strips, all subsets ending at the free upper/lower edge.
            capacities=[]
            for ordered,start in [(ys,-c.ext_top),([-y for y in reversed(ys)],-(b.d+c.ext_bottom))]:
                for j,y in enumerate(ordered,1):
                    lv=y-start;Agv=lv*t;Anv=max(0,lv-(j-.5)*c.dn)*t;Ant=max(0,(width-c.gauge-c.dn)/2)*t
                    rr=2*min(.6*fu*Anv+.5*fu*Ant,.6*fy*Agv+.5*fu*Ant)/G2
                    capacities.append((rr*nb/(2*j),lv,j,rr))
            Rc,lv,j,rr=min(capacities)
            add('block_plate','Chapa — rasgamento de blocos parciais e completos',abs(V),Rc,'N',NBR+', 6.5.6','Rbloco=2 min(0,6 fu Anv+0,5 fu Ant;0,6 fy Agv+0,5 fu Ant)/γa2',f'Bloco de {j} linhas por lado; lv={lv:.3f}; Rbloco={rr:.3f}; resistência equivalente ao V total={Rc:.3f}', 'São percorridos os blocos que terminam nas bordas superior e inferior. Demanda de cada bloco proporcional ao número de parafusos contidos; Ct=0,5 conservador.')
    Rv,cv=web_shear(b.clear,b.tw,sb.fy)
    add('beam_web','Viga — cisalhamento da alma',abs(V),Rv,'N',NBR+', 5.4.3','VRd=0,6 fy h tw Cv/γa1',f'h={b.clear:g}; tw={b.tw:g}; Cv={cv:.5f}; VRd={Rv:.3f}', 'Alma sem furos na ligação de topo; sem ganho por enrijecedores.')
    if c.kind=='pinned':
        # Axial is deliberately assigned to the connected web strip.
        sigma=abs(N)/(b.clear*b.tw);tau=1.5*abs(V)/(b.clear*b.tw)
        add('beam_nv','Alma da viga — interação local N e V',math.hypot(sigma,math.sqrt(3)*tau),sb.fy/G1,'MPa',NBR+', 6.5; modelo elástico','σeq=√[(N/Aw)²+3(1,5V/Aw)²]',f'Aw={b.clear*b.tw:.3f}; σ={sigma:.4f}; τ={tau:.4f}', 'Conservador: sem crédito às mesas para o esforço axial. Compressão global da viga é externa ao modelo local.')
    # Compression on column flange and column web, no direct beam/column contact.
    fc=max(max(C,0),max(N,0) if c.kind=='pinned' else T)
    ln=0. if c.kind=='moment' else b.clear
    Ry=1.10*(2.5*s.tf+ln)*sc.fy*s.tw/G1
    add('column_web_yield','Coluna — escoamento local da alma',fc,Ry,'N',NBR+', 5.7.3.2(b)','FRd=1,10(2,5k+ln) fyc twc/γa1',f'k=tf={s.tf:g}; ln={ln:g}; FRd={Ry:.3f}; F={fc:.3f}', 'Sem crédito ao raio e ao espalhamento da força nas ligações com momento; caso de extremidade conservador.')
    add('column_crippling','Coluna — enrugamento da alma sob compressão',max(C,0),crippling_point(s.tw,s.tf,sc.fy),'N',NBR+', 5.7.4.2(b)','FRd=0,33 twc² √(E fyc tfc/twc)/γa1',f'twc={s.tw:g}; tfc={s.tf:g}; C={max(C,0):.3f}', 'Resistência mínima, sem crédito ao comprimento carregado ou à posição interna da carga.')
    Rc=min(sp.fy,sc.fy)/G1*b.bf*b.tf
    add('contact','Chapa e coluna — compressão local de contato',max(C,0),Rc,'N',NBR+', 6.5; equilíbrio local','CRd=min(fyp;fyc) bf tf/γa1',f'Acontato=bf tf={b.bf*b.tf:.3f}; CRd={Rc:.3f}', 'Contato considerado somente sobre a área de uma mesa da viga, conservador para a rotulada em compressão; placa em contato com a coluna.')
    if c.kind=='moment':
        # Pure panel shear is a lower-bound contribution; its boundary conditions
        # and absence of significant column axial compression remain explicit.
        Rp,cp=web_shear(s.clear,s.tw,sc.fy)
        demand=abs(M)/(b.d-b.tf)+abs(N)/2
        add('panel','Coluna — cisalhamento do painel da alma',demand,Rp,'N',NBR+', 5.4.3 e 5.7.7; parcela conservadora da alma','Vp=|M|/(d−tf)+|N|/2; VRd=0,6 fyc hc twc Cv/γa1',f'Vp={demand:.3f}; hc={s.clear:g}; Cv={cp:.5f}; VRd={Rp:.3f}', 'Sem ganho das mesas da coluna nem dedução do cortante favorável da coluna; hipótese de Ncol,Sd ≤ 0,4 Ag,col fy,col declarada nas premissas.')
    return rows,a


def evaluate(c):
    issues=validate(c);r=Result(issues=issues)
    if any(i.severity=='error' for i in issues):return r
    actual,aa=_calculate(c,c.V,c.N,c.M,'Entrada')
    result=math.hypot(c.N,c.V)
    # Minimum-force check keeps the complete proportional load path when nonzero.
    f=max(1,45000/result) if c.norm_minimum and result>0 else 1.
    r.actual=actual;r.minimum_factor=f
    r.checks,a=_calculate(c,c.V*f,c.N*f,c.M,'Mínimo de força' if f>1 else 'Entrada')
    if c.kind=='moment' and abs(c.N*f)*(c.beam.d-c.beam.tf)>abs(c.M):
        r.issues.append(Issue('error','A conferência mínima de força ultrapassa o domínio de axial do DG39; revisar o modelo da ligação.',DG+', 3.5'))
        r.checks=[];r.actual=[];return r
    r.geometry={'actions':a,'actual_actions':aa,'rows':c.rows,'hp':c.hp,'nb':c.count}
    return r


def presets():
    p=profiles();b=p['W 410 x 38,8'];s=p['CS 600 x 281']
    return {
        'Rotulada · V e tração':EndPlate(b,s),
        'Rotulada · V e compressão':EndPlate(b,s,N=-2000.),
        'Engastada · extensão acima e abaixo':EndPlate(b,s,kind='moment',tp=19.05,bp=160.,M=40000000.,V=40000.,project='End plate engastada estendida nos dois lados'),
        'Engastada · extensão somente acima':EndPlate(b,s,kind='moment',layout='top',tp=19.05,bp=160.,M=40000000.,V=40000.,project='End plate engastada estendida acima'),
    }
