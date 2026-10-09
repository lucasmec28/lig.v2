"""Interface independente para a emenda com duas talas."""
from dataclasses import fields
import hashlib
import json
import pandas as pd
import streamlit as st
from .models import profiles,Profile,STEELS,BOLTS,DIAMETERS,KGF,VERSION
from .double_cover import DoubleCoverConnection,presets,evaluate,PLATE_STOCK,ASSEMBLY_NOTE
from .double_cover_drawing import image_bytes
from .report import BRAND,LINK,number,display

P=profiles();PRESETS=presets()

def seed(c):
    s=st.session_state
    for f in fields(c):
        if f.name not in ('beam','support','V','N'):s['dc_'+f.name]=getattr(c,f.name)
    s['dc_V_kgf']=c.V/KGF;s['dc_N_kgf']=c.N/KGF
    s['dc_db_label']=next(k for k,v in DIAMETERS.items() if abs(c.db-v)<1e-6)
    for key in ('fin_t','cover_t','stiffener_t'):
        s['dc_'+key+'_label']=next((k for k,v in PLATE_STOCK.items() if abs(getattr(c,key)-v)<1e-6),'Personalizada')
    for key in ('beam','support'):
        p=getattr(c,key);s['dc_'+key+'_name']=p.name if p.name in P else 'Seção I personalizada'
        s['dc_'+key+'_manual_name']=p.name
        for k in ('d','bf','tw','tf','clear'):s['dc_'+key+'_'+k]=float(getattr(p,k))
    s.pop('dc_report',None)

def load_example():seed(PRESETS[st.session_state.dc_example])

def load_json():
    try:
        up=st.session_state.dc_upload
        if up is None:raise ValueError('Selecione um arquivo JSON.')
        if len(up.getvalue())>200000:raise ValueError('Projeto maior que o limite de 200 kB.')
        c=DoubleCoverConnection.from_dict(json.loads(up.getvalue()))
        r=evaluate(c)
        if any(x.severity=='error' for x in r.issues):raise ValueError('; '.join(x.text for x in r.issues if x.severity=='error'))
        seed(c);st.session_state.pop('dc_import_error',None)
    except (ValueError,TypeError,KeyError,OverflowError) as exc:st.session_state.dc_import_error='Não foi possível abrir: '+str(exc)

def profile_changed(key):
    p=P.get(st.session_state['dc_'+key+'_name'])
    if p:st.session_state['dc_'+key+'_steel']='ASTM A36' if p.family in ('CS','CVS','VS','Soldado') else 'ASTM A572 Gr.50'

def profile_widget(key,label):
    name=st.selectbox(label,['Seção I personalizada']+list(P),key='dc_'+key+'_name',on_change=profile_changed,args=(key,))
    if name in P:return P[name]
    with st.expander('Dimensões de '+label.lower(),expanded=True):
        name=st.text_input('Designação',key='dc_'+key+'_manual_name')
        vals={}
        for k,label in [('d','Altura d'),('bf','Largura bf'),('tw','Alma tw'),('tf','Mesa tf'),('clear','Altura livre sem concordâncias')]:
            vals[k]=st.number_input(label+' (mm)',min_value=.1,max_value=3000.,key='dc_'+key+'_'+k)
        a=2*vals['bf']*vals['tf']+(vals['d']-2*vals['tf'])*vals['tw']
        return Profile(name,'Soldado',max(a,1)*.00785,area=max(a,1),**vals)

def stock_changed(key):
    label=st.session_state['dc_'+key+'_label']
    if label in PLATE_STOCK:st.session_state['dc_'+key]=PLATE_STOCK[label]

def thickness(key,label):
    lab=st.selectbox(label,list(PLATE_STOCK)+['Personalizada'],key='dc_'+key+'_label',on_change=stock_changed,args=(key,))
    if lab=='Personalizada':return st.number_input(label+' (mm)',min_value=.1,max_value=100.,key='dc_'+key,format='%.4f')
    st.caption(number(PLATE_STOCK[lab],4)+' mm')
    return PLATE_STOCK[lab]

def render():
    from .double_cover_report import create_report
    if 'dc_beam_name' not in st.session_state:seed(next(iter(PRESETS.values())))
    with st.sidebar:
        st.markdown('### LRO Ligações')
        st.caption('Versão '+VERSION+' · modelo por componentes')
        st.selectbox('Exemplos',list(PRESETS),key='dc_example')
        st.button('Usar exemplo de duas talas',on_click=load_example,use_container_width=True)
        st.file_uploader('Abrir projeto desta ligação',type=['json'],key='dc_upload')
        st.button('Abrir projeto de duas talas',on_click=load_json,use_container_width=True)
        if 'dc_import_error' in st.session_state:st.error(st.session_state.dc_import_error)
        st.divider();st.caption(BRAND);st.link_button('LinkedIn · Lucas Oliveira',LINK)
    st.markdown('<div class="eyebrow">LIGAÇÃO ROTULADA · PERFIS I</div>',unsafe_allow_html=True)
    st.title('Viga na alma de coluna')
    st.caption('Duas talas parafusadas · nervura soldada · quatro enrijecedores horizontais')
    st.text_input('Identificação do projeto',key='dc_project')
    left,right=st.columns([.95,1.55],gap='large')
    with left:
        beam=profile_widget('beam','Viga apoiada');support=profile_widget('support','Coluna')
        a,b=st.columns(2)
        with a:V=st.number_input('Cortante vertical V (kgf)',key='dc_V_kgf',format='%.2f')*KGF
        with b:N=st.number_input('Axial N (kgf)',key='dc_N_kgf',format='%.2f')*KGF
        st.caption('Esforços já majorados. N positivo: tração; N negativo: compressão. Sem momento externo aplicado.')
        a,b=st.columns(2)
        with a:
            st.selectbox('Parafuso Ø (pol.)',list(DIAMETERS),key='dc_db_label')
            st.number_input('Linhas por grupo',min_value=2,max_value=12,key='dc_n')
            st.number_input('Passo vertical p (mm)',min_value=1.,key='dc_pitch')
        with b:
            st.selectbox('Classe do parafuso',[x for x in BOLTS if x!='ASTM A307'],key='dc_bolt')
            st.number_input('Borda vertical eᵥ (mm)',min_value=1.,key='dc_edge_v')
            st.number_input('Borda horizontal e (mm)',min_value=1.,key='dc_edge_x')
        st.caption('Uma coluna de parafusos em cada grupo, mesma quantidade e passo. Duas talas iguais, centradas na altura da viga.')
        a,b=st.columns(2)
        with a:tn=thickness('fin_t','Espessura da nervura')
        with b:tt=thickness('cover_t','Espessura das talas')
        nearest=min(PLATE_STOCK,key=lambda k:abs(PLATE_STOCK[k]-beam.tw))
        st.caption(f'Alma da viga: {number(beam.tw,3)} mm. Chapa de estoque mais próxima: {nearest}; conferir também a compatibilidade dos filetes.')
        with st.expander('Geometria e montagem'):
            st.number_input('Folga g entre nervura e viga (mm)',min_value=.1,key='dc_gap')
            st.number_input('Projeção u além da mesa da coluna (mm)',min_value=1.,key='dc_extension')
            st.number_input('Distância livre H entre horizontais (mm)',min_value=1.,key='dc_root_height')
            th=thickness('stiffener_t','Espessura dos quatro horizontais')
            st.number_input('Alívio de canto dos horizontais c (mm)',min_value=0.,key='dc_corner_clip')
            st.selectbox('Ajuste de espessuras',['automatic','fit'],key='dc_shim_mode',format_func=lambda x:'Calços simétricos na peça mais fina' if x=='automatic' else 'Pequena diferença admitida na montagem')
            if st.session_state.dc_shim_mode=='fit':st.number_input('Tolerância adotada de espessura (mm)',min_value=0.,max_value=1.,key='dc_fit_tolerance')
            st.number_input('Folga de montagem (mm)',min_value=0.,key='dc_clearance')
            st.number_input('Raio livre para porca/ferramenta (mm)',min_value=.1,key='dc_tool_radius')
        with st.expander('Soldas de oficina'):
            st.caption('Filetes duplos no conjunto soldado. As talas e a viga não recebem soldas de ligação.')
            st.number_input('Nervura → alma da coluna, w (mm)',min_value=.1,key='dc_weld_web')
            st.number_input('Nervura → horizontais, w (mm)',min_value=.1,key='dc_weld_fin_stiffener')
            st.number_input('Horizontais → coluna, w (mm)',min_value=.1,key='dc_weld_stiffener_column')
            st.number_input('Resistência do eletrodo fw (MPa)',min_value=1.,key='dc_fw')
        with st.expander('Materiais e critérios'):
            for key,label,p in [('beam_steel','Aço da viga',beam),('support_steel','Aço da coluna',support),('fin_steel','Aço da nervura',None),('cover_steel','Aço das talas',None),('stiffener_steel','Aço dos horizontais',None)]:
                plate=p is None or p.family in ('VS','CVS','CS','Soldado')
                options=[k for k,s in STEELS.items() if s.plate_allowed] if plate else [k for k,s in STEELS.items() if s.rolled_allowed]
                st.selectbox(label,options,key='dc_'+key)
            st.checkbox('Rosca incluída nos planos de corte',key='dc_threads')
            st.checkbox('Furos executados com broca, sem acréscimo de 2 mm na dedução líquida',key='dc_drilled')
            st.checkbox('Conferir mínimo resistente de 45 kN',key='dc_norm_minimum')
            st.caption('Contenção eficaz da viga e penetração total das juntas internas dos perfis soldados são premissas fixas. Sem atrito, fadiga ou ações cíclicas.')
        with st.expander('Observações do projeto'):st.text_area('Observações',key='dc_notes')
    values={f.name:st.session_state['dc_'+f.name] for f in fields(DoubleCoverConnection) if f.name not in ('beam','support','V','N','db','fin_t','cover_t','stiffener_t')}
    c=DoubleCoverConnection(beam,support,V=V,N=N,db=DIAMETERS[st.session_state.dc_db_label],fin_t=tn,cover_t=tt,stiffener_t=th,**values)
    r=evaluate(c);encoded=json.dumps(c.to_dict(),ensure_ascii=False,indent=2);digest=hashlib.sha256(encoded.encode()).hexdigest()
    if st.session_state.get('dc_report',('','',b''))[0]!=digest:st.session_state.pop('dc_report',None)
    with right:
        if r.status in ('GEOMETRIA INVÁLIDA','NÃO ATENDE'):st.error(r.status)
        elif any(i.severity in ('pending','interference') for i in r.issues):st.warning(r.status)
        else:st.success(r.status)
        if r.governing:
            a,b=st.columns(2)
            a.metric('Maior índice calculado',number(r.governing.ratio,3))
            b.metric('Verificações de componentes',len(r.checks))
            st.caption(r.governing.name+' · '+r.governing.case)
        can_draw=bool(r.geometry)
        if can_draw:
            st.image(image_bytes(c),width='stretch')
        for issue in r.issues:
            if issue.severity=='excluded':continue
            if issue.severity=='error':st.error(issue.text)
            elif issue.severity in ('pending','interference'):st.warning(issue.text)
            else:st.caption(issue.text)
        if r.minimum_factor>1:
            st.info('Além da entrada, o app confere a resultante mínima resistente de 45 kN, mantendo a direção N/V. Fator da conferência mínima: '+number(r.minimum_factor,3)+'. Não é nova majoração das ações.')
        if r.checks:
            a=r.geometry['actual_actions']
            with st.expander('Equilíbrio e ações transmitidas à coluna'):
                st.write('Rótula nominal no meio da folga. A excentricidade gera momento local no conjunto soldado, mesmo sem momento externo informado.')
                st.write(f'e até a face da alma = {number(c.pin_x)} mm; M local = {number(a["M"]/(KGF*1000))} kgf·m.')
                st.write(f'H superior = {number(a["top"]/KGF)} kgf; H inferior = {number(a["bottom"]/KGF)} kgf.')
                st.caption('Valores acima correspondem às ações de entrada. O dimensionamento também inclui a conferência mínima, se ativa. A verificação global da coluna pertence ao modelo da estrutura.')
    if r.checks:
        st.subheader('Resultados dos componentes')
        data=[]
        for row in r.checks:
            sd,unit=display(row.demand,row.unit);rd,_=display(row.resistance,row.unit)
            data.append({'Verificação':row.name,'Solicitação':sd,'Resistência / limite':rd,'Unidade':unit,'Índice':round(row.ratio,3),'Resultado':'Atende' if row.passed else 'Não atende','Caso':row.case})
        st.dataframe(pd.DataFrame(data),hide_index=True,width='stretch')
        with st.expander('Equações, substituições e referências'):
            for row in r.checks:
                st.markdown('**'+row.name+'**');st.code(row.equation,language=None);st.caption(row.substitution+' | '+row.variables);st.caption(row.reference)
    st.subheader('Salvar projeto e memória')
    a,b,cx=st.columns(3)
    a.download_button('Baixar projeto JSON',encoded,'Ligacao_duas_talas_LRO.json','application/json',use_container_width=True)
    if can_draw:b.download_button('Baixar desenho SVG',image_bytes(c,'svg'),'Ligacao_duas_talas_LRO.svg','image/svg+xml',use_container_width=True)
    detailed=st.checkbox('Memória detalhada: todas as substituições',key='dc_detailed')
    if cx.button('Gerar memória de duas talas',disabled=not bool(r.checks),use_container_width=True):
        st.session_state.dc_report=(digest,detailed,create_report(c,r,detailed))
    saved=st.session_state.get('dc_report')
    if saved and saved[0]==digest and saved[1]==detailed:
        st.download_button('Baixar memória de duas talas .docx',saved[2],'Memoria_duas_talas_LRO.docx','application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    st.divider()
    st.subheader('Premissas adotadas')
    st.write('Modelo plano, contenção eficaz da viga e juntas internas dos perfis soldados com penetração total. Análise global dos membros, fadiga, atrito e ações cíclicas permanecem fora do modelo local.')
    st.write(ASSEMBLY_NOTE)
    for issue in r.issues:
        if issue.severity=='excluded' and issue.text!=ASSEMBLY_NOTE:st.write(issue.text)
    st.caption(BRAND)
