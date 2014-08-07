from Models.uv_object import UnveillanceObject
from conf import DEBUG

class UnveillanceText(UnveillanceObject):
	def __init__(self, _id=None, inflate=None, emit_sentinels=None):
		if inflate is not None:
			from lib.Core.Utils.funcs import generateMD5Hash
			from conf import UUID
			from vars import UV_DOC_TYPE, MIME_TYPES
			
			inflate['_id'] = generateMD5Hash(content=inflate['media_id'], 
				salt=MIME_TYPES['txt'])
			
			inflate['farm'] = UUID
			inflate['uv_doc_type'] = UV_DOC_TYPE['DOC']
			inflate['mime_type'] = MIME_TYPES['txt']
		
		super(UnveillanceText, self).__init__(_id=_id, 
			inflate=inflate, emit_sentinels=emit_sentinels)
			
	