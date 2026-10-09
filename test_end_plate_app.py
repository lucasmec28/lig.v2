from pathlib import Path
import json
from streamlit.testing.v1 import AppTest
from lro.end_plate import presets
APP=Path(__file__).resolve().parents[1]/'app.py'

def open_app(kind):
    at=AppTest.from_file(str(APP),default_timeout=45).run()
    at.selectbox(key='connection_family').set_value('End plate · '+kind).run()
    assert not at.exception
    return at

def test_pin_and_moment_inputs_and_export_invalidation():
    at=open_app('rotulada')
    assert not at.error and len(at.success)>0
    assert not any('momento' in x.label.lower() or 'M maior' in x.label for x in at.number_input)
    next(x for x in at.button if x.label=='Gerar memória Word').click().run()
    assert not at.exception and at.session_state['ep_report'][2][:2]==b'PK'
    at.number_input(key='ep_gauge').set_value(50.).run()
    assert not at.exception and at.error
    assert not any(getattr(x,'label','')=='Baixar memória Word' for x in at.get('download_button'))
    at.selectbox(key='connection_family').set_value('End plate · engastada').run()
    assert not at.exception and not at.error
    assert at.number_input(key='ep_M_kgfm')
    at.selectbox(key='ep_layout').set_value('top').run()
    assert not at.exception and not at.error
    at.number_input(key='ep_M_kgfm').set_value(-1000.).run()
    assert at.error and next(x for x in at.button if x.label=='Gerar memória Word').disabled


def test_moment_project_import_restores_signed_loads():
    at=open_app('engastada');c=list(presets().values())[2]
    at.get('file_uploader')[0].upload('endplate.json',json.dumps(c.to_dict()).encode(),'application/json').run()
    next(x for x in at.button if x.label=='Abrir projeto de end plate').click().run()
    assert not at.exception and not at.error
