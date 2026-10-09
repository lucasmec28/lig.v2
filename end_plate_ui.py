"""Entradas em kgf, kgf·m e mm; motor independente da interface."""
from dataclasses import fields,asdict
import json,hashlib
import pandas as pd
import streamlit as st
from .models import profiles,STEELS,BOLTS,DIAMETERS,KGF,VERSION
from .end_plate import EndPlate,STOCK,presets,evaluate
from .end_plate_drawing import image_bytes
from .report import BRAND,LINK,number,display

P=profiles();EXAMPLES=presets()

def seed(c):
    s=st.session_state
    s.ep_model=asdict(c);s.ep_screen_kind=c.kind
    for f in fields(c):
        if f.name not in ('beam','support','V','N','M'):s['ep_'+f.name]=getattr(c,f.name)
    for k in ('beam','support'):s['ep_'+k+'_name']=getattr(c,k).name
    s.ep_V_kgf=c.V/KGF;s.ep_N_kgf=c.N/KGF;s.ep_M_kgfm=c.M/(1000*KGF)
    s.ep_db_label=next(k for k,v in DIAMETERS.items() if v==c.db)
    s.ep_t_label=next((k for k,v in STOCK.items() if v==c.tp),'Personalizada')
    s.pop('ep_report',None)

def load_example():
    c=EXAMPLES[st.session_state.ep_example];seed(c)
    st.session_state.connection_family='End plate · '+('rotulada' if c.kind=='pinned' else 'engastada')

def load_json():
    try:
        up=st.session_state.ep_upload
        if up is None:raise ValueError('Selecione um projeto JSON.')
        if len(up.getvalue())>200000:raise ValueError('Projeto maior que 200 kB.')
        c=EndPlate.from_dict(json.loads(up.getvalue()))
        if c.beam.name not in P or c.support.name not in P:raise ValueError('Esta interface utiliza seções do catálogo.')
        if c.beam!=P[c.beam.name] or c.support!=P[c.support.name]:raise ValueError('Dimensões dos perfis diferem do catálogo. O arquivo não será alterado silenciosamente.')
        r=evaluate(c)
        if any(i.severity=='error' for i in r.issues):raise ValueError('; '.join(i.text for i in r.issues if i.severity=='error'))
        seed(c);st.session_state.connection_family='End plate · '+('rotulada' if c.kind=='pinned' else 'engastada');st.session_state.pop('ep_import_error',None)
    except (ValueError,TypeError,KeyError,OverflowError,AttributeError) as exc:st.session_state.ep_import_error=str(exc)

def stock_change():
    if st.session_state.ep_t_label in STOCK:st.session_state.ep_tp=STOCK[st.session_state.ep_t_label]

def profile_change(key):
    p=P[st.session_state['ep_'+key+'_name']]
    st.session_state['ep_'+key+'_steel']='ASTM A36' if p.family in ('CS','CVS','VS','Soldado') else 'ASTM A572 Gr.50'

def render(kind):
    from .end_plate_report import create_report
    if st.session_state.get('ep_screen_kind')!=kind:
        seed(next(c for c in EXAMPLES.values() if c.kind==kind));st.session_state.ep_screen_kind=kind
    with st.sidebar:
        st.caption('LRO Ligações '+VERSION)
        st.selectbox('Exemplos de end plate',list(EXAMPLES),key='ep_example')
        st.button('Carregar exemplo',on_click=load_example,use_container_width=True)
        st.file_uploader('Projeto de end plate',type=['json'],key='ep_upload')
        st.button('Abrir projeto de end plate',on_click=load_json,use_container_width=True)
        if 'ep_import_error' in st.session_state:st.error(st.session_state.ep_import_error)
        st.divider();st.caption(BRAND);st.link_button('LinkedIn · Lucas Oliveira',LINK)
    # A loaded example can change the connection kind; the header tracks the object.
    k=st.session_state.ep_kind
    st.title('End plate '+('rotulada' if k=='pinned' else 'engastada'))
    st.caption('Viga na mesa de coluna · perfis I · análise plana · uma combinação de cálculo')
    st.text_input('Identificação do projeto',key='ep_project')
    left,right=st.columns([.95,1.5],gap='large')
    with left:
        st.subheader('Perfis e esforços')
        st.selectbox('Viga',list(P),key='ep_beam_name',on_change=profile_change,args=('beam',))
        st.selectbox('Coluna',list(P),key='ep_support_name',on_change=profile_change,args=('support',))
        b=P[st.session_state.ep_beam_name];s=P[st.session_state.ep_support_name]
        x,y=st.columns(2)
        with x:V=st.number_input('V vertical (kgf)',key='ep_V_kgf',format='%.2f')*KGF
        with y:N=st.number_input('N axial (kgf)',key='ep_N_kgf',format='%.2f')*KGF
        M=st.number_input('M maior inércia (kgf·m)',key='ep_M_kgfm',format='%.2f')*1000*KGF if k=='moment' else 0.
        st.caption('Esforços já majorados. N positivo: tração; N negativo: compressão.'+(' M positivo: tração na mesa superior; negativo: mesa inferior.' if k=='moment' else ' Sem momento externo.'))
        st.subheader('Chapa e parafusos')
        if k=='moment':st.selectbox('Extensão da chapa',['both','top'],key='ep_layout',format_func=lambda v:'Acima e abaixo' if v=='both' else 'Somente acima')
        x,y=st.columns(2)
        with x:
            st.selectbox('Espessura da chapa (pol.)',list(STOCK)+['Personalizada'],key='ep_t_label',on_change=stock_change)
            if st.session_state.ep_t_label=='Personalizada':tp=st.number_input('Espessura tp (mm)',min_value=.1,max_value=100.,key='ep_tp')
            else:tp=STOCK[st.session_state.ep_t_label];st.caption(number(tp,4)+' mm')
            st.number_input('Largura bp (mm)',min_value=1.,key='ep_bp')
        with y:
            st.selectbox('Parafusos Ø (pol.)',list(DIAMETERS),key='ep_db_label')
            st.number_input('Gabarito g (mm)',min_value=1.,key='ep_gauge')
        if k=='pinned':
            x,y=st.columns(2)
            with x:st.number_input('Linhas de parafusos',min_value=2,max_value=10,key='ep_n')
            with y:st.number_input('Passo p (mm)',min_value=1.,key='ep_pitch')
            st.number_input('Sobra acima e abaixo (mm)',min_value=.1,max_value=10.,key='ep_overhang')
            st.caption('Grupo centrado, duas colunas de parafusos entre as mesas da viga.')
        else:
            x,y=st.columns(2)
            with x:st.number_input('Mesa → linha externa pfo (mm)',min_value=1.,key='ep_pfo')
            with y:st.number_input('Mesa → linha interna pfi (mm)',min_value=1.,key='ep_pfi')
            st.number_input('Linha externa → borda e (mm)',min_value=1.,key='ep_edge')
            st.caption('4E: quatro parafusos na região tracionada, mais os parafusos do lado comprimido. A altura da chapa é calculada automaticamente.')
        with st.expander('Soldas e montagem'):
            if k=='pinned':
                st.number_input('Filete contínuo w (mm)',min_value=.1,key='ep_weld')
                st.checkbox('Bordas com reforço de solda',key='ep_reinforced_edge')
            else:st.write('Mesas e alma da viga soldadas à chapa por juntas de penetração total, com metal de adição compatível.')
            st.number_input('Resistência do eletrodo fw (MPa)',min_value=1.,key='ep_fw')
            st.number_input('Raio de ferramenta/porca (mm)',min_value=1.,key='ep_tool_radius')
        with st.expander('Materiais e critérios'):
            for key,label,p in [('beam_steel','Aço da viga',b),('support_steel','Aço da coluna',s),('plate_steel','Aço da chapa',None)]:
                welded=p is None or p.family in ('CS','CVS','VS','Soldado')
                options=[x for x,v in STEELS.items() if v.plate_allowed] if welded else [x for x,v in STEELS.items() if v.rolled_allowed]
                st.selectbox(label,options,key='ep_'+key)
            st.selectbox('Classe dos parafusos',[x for x in BOLTS if x!='ASTM A307'],key='ep_bolt')
            st.checkbox('Rosca no plano de corte',key='ep_threads')
            st.checkbox('Furos com broca, sem acréscimo de 2 mm na área líquida',key='ep_drilled')
            st.checkbox('Conferir resistência mínima de 45 kN',key='ep_norm_minimum')
        with st.expander('Observações'):st.text_area('Observações do projeto',key='ep_notes')
    excluded=('beam','support','V','N','M','db','tp')
    values={f.name:st.session_state.get('ep_'+f.name,st.session_state.ep_model[f.name]) for f in fields(EndPlate) if f.name not in excluded}
    c=EndPlate(b,s,V=V,N=N,M=M,db=DIAMETERS[st.session_state.ep_db_label],tp=tp,**values)
    st.session_state.ep_model=asdict(c)
    r=evaluate(c);encoded=json.dumps(c.to_dict(),ensure_ascii=False,indent=2,allow_nan=False);digest=hashlib.sha256(encoded.encode()).hexdigest()
    with right:
        if r.status in ('GEOMETRIA INVÁLIDA','NÃO ATENDE'):st.error(r.status)
        elif any(i.severity in ('pending','interference') for i in r.issues):st.warning(r.status)
        else:st.success(r.status)
        st.image(image_bytes(c),width='stretch')
        for issue in r.issues:
            if issue.severity=='excluded':continue
            if issue.severity=='error':st.error(issue.text)
            elif issue.severity in ('pending','interference'):st.warning(issue.text)
        if r.checks:
            a=r.geometry['actions'];x,y,z=st.columns(3)
            x.metric('Maior índice',number(max(row.ratio for row in r.checks),3))
            y.metric('tp mínimo calculado',number(a['tp_required'],2)+' mm')
            z.metric('Parafusos',c.count)
            if k=='moment':st.caption('Espessura mínima pelo método de chapa espessa do DG39; o resultado também depende da mesa da coluna e das demais verificações.')
            else:st.caption('tp mínimo refere-se à tração sem alavanca; o limite máximo de espessura para a rótula é verificado separadamente.')
            if r.minimum_factor>1:st.info('Conferência adicional de força mínima: V e N multiplicados por '+number(r.minimum_factor,3)+'. O momento externo permanece igual à entrada; não há nova majoração da combinação.')
        st.subheader('Salvar e exportar')
        st.download_button('Salvar projeto JSON',encoded,'Projeto_LRO_end_plate.json','application/json',use_container_width=True)
        st.download_button('Desenho vetorial SVG',image_bytes(c,'svg'),'End_plate_LRO.svg','image/svg+xml',use_container_width=True)
        detailed=st.checkbox('Memória detalhada',key='ep_detailed')
        if st.button('Gerar memória Word',type='primary',disabled=not bool(r.checks),use_container_width=True):
            st.session_state.ep_report=(digest,detailed,create_report(c,r,detailed))
        saved=st.session_state.get('ep_report')
        if saved and saved[:2]==(digest,detailed):st.download_button('Baixar memória Word',saved[2],'Memoria_end_plate_LRO.docx','application/vnd.openxmlformats-officedocument.wordprocessingml.document',use_container_width=True)
    st.subheader('Verificações')
    if r.checks:
        rows=[]
        for row in r.checks:
            sd,u=display(row.demand,row.unit);rd,_=display(row.resistance,row.unit)
            rows.append({'Verificação':row.name,'Tipo':row.category,'Sd / valor':sd,'Rd / limite':rd,'Unidade':u,'Índice':row.ratio,'Resultado':'Atende' if row.passed else 'Não atende'})
        st.dataframe(pd.DataFrame(rows),hide_index=True,width='stretch',column_config={'Índice':st.column_config.NumberColumn(format='%.3f')})
        with st.expander('Equações e referências'):
            for row in r.checks:st.markdown('**'+row.name+'**');st.write(row.equation);st.write(row.substitution);st.caption(row.variables+' '+row.reference)
    st.divider();st.subheader('Premissas adotadas')
    for note in c.assumptions:st.write(note)
    for issue in r.issues:
        if issue.severity=='excluded':st.write(issue.text)
    st.caption(BRAND);st.link_button('Contato no LinkedIn',LINK)
