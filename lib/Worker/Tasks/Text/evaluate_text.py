from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def evaluateText(task):
	task_tag = "TEXT EVALUATION"
	print "\n\n************** %s [START] ******************\n" % task_tag
	print "evaluating text at %s" % task.doc_id
	task.setStatus(412)
	
	from lib.Worker.Models.uv_document import UnveillanceDocument
	from conf import DEBUG
	from vars import MIME_TYPE_TASKS
	
	document = UnveillanceDocument(_id=task.doc_id)
	if DEBUG: print document.emit()
	
	"""
		limited choices: json, pgp, or txt
	"""
	if not document.getFile(document.file_name): return
	
	content = document.loadFile(document.file_name)
	if content is None: return
	
	new_mime_type = None
	import json
	try:
		json_txt = json.loads(content)
		new_mime_type = "application/json"
		
		print "THIS IS JSON"
	except Exception as e:
		print "NOT JSON: %s" % e
	
	task_path = None	
	if new_mime_type is not None:
		document.mime_type = new_mime_type
		document.save()
		
		if document.mime_type in MIME_TYPE_TASKS.keys():
			task_path = MIME_TYPE_TASKS[document.mime_type][0]
	else:
		try:
			from lib.Core.Utils.funcs import cleanLine
			from vars import ASSET_TAGS
			
			txt_json = []
			for line in content.splitlines(): 
				if DEBUG: 
					print "parsing line..."
					print line
				txt_json.append(cleanLine(line))
			
			if DEBUG: print txt_json
			
			document.addAsset(txt_json, "doc_texts.json", as_literal=False,
				description="jsonified text of original document, segment by segment",
				tags=[ASSET_TAGS['TXT_JSON']])

			task_path = MIME_TYPE_TASKS[document.mime_type][1]
		except Exception as e: 
			if DEBUG:
				print "ERROR HERE GENERATING DOC TEXTS:"
				print e
	
	if task_path is not None:
		from lib.Worker.Models.uv_task import UnveillanceTask
		from conf import UUID
		
		new_task = UnveillanceTask(inflate={
			'doc_id' : document._id,
			'task_path' : task_path,
			'queue' : UUID})
		
		new_task.run()
	
	task.finish()
	print "\n\n************** %s [END] ******************\n" % task_tag