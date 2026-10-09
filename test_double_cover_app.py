import json
from pathlib import Path
from streamlit.testing.v1 import AppTest
from lro.double_cover import presets
from lro.models import KGF

APP=Path(__file__).resolve().parents[1]/'app.py'
def open_app():
    at=AppTest.from_file(str(APP),default_timeout=30).run()
    at.selectbox(key='connection_family').set_value('Alma de coluna · duas talas').run()
    assert not at.exception
    return at

def test_new_type_export_and_invalidate_old_report():
    at=open_app()
    assert any(x.value=='ATENDE ÀS VERIFICAÇÕES REALIZADAS' for x in at.success)
    assert not at.error
    assert not any('momento' in x.label.lower() for x in at.number_input)
    at.button[0] # widgets present
    next(x for x in at.button if x.label=='Gerar memória de duas talas').click().run()
    assert not at.exception
    assert at.session_state['dc_report'][2][:2]==b'PK'
    at.number_input(key='dc_pitch').set_value(20.).run()
    assert not at.exception
    assert any(x.value=='GEOMETRIA INVÁLIDA' for x in at.error)
    assert next(x for x in at.button if x.label=='Gerar memória de duas talas').disabled
    assert not any(getattr(x,'label','')=='Baixar memória de duas talas .docx' for x in at.get('download_button'))

def test_compression_import_and_switch_family_retains_old_type():
    at=open_app();c=list(presets().values())[1]
    at.get('file_uploader')[0].upload('compressao.json',json.dumps(c.to_dict()).encode(),'application/json').run()
    next(x for x in at.button if x.label=='Abrir projeto de duas talas').click().run()
    assert not at.exception and not at.error
    assert at.number_input(key='dc_N_kgf').value==c.N/KGF
    at.selectbox(key='connection_family').set_value('Single plate').run()
    assert not at.exception and len(at.success)>0

def test_thickness_change_changes_live_geometry_and_fit_warning():
    at=open_app()
    at.selectbox(key='dc_fin_t_label').set_value('3/8"').run()
    assert not at.exception and not at.error
    assert at.session_state['dc_fin_t']==9.525
    at.selectbox(key='dc_shim_mode').set_value('fit').run()
    assert not at.exception and any('Diferença de espessuras' in x.value for x in at.error)
    at.selectbox(key='dc_support_name').set_value('CS 600 x 281').run()
    assert not at.exception
    assert at.selectbox(key='dc_support_steel').value=='ASTM A36'
