from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def compileMetadata(task):
	print "\n\n************** COMPILING METADATA [START] ******************\n"
	print "compiling metadata for %s" % task.doc_id
	task.setStatus(412)
	
	from lib.Worker.Models.uv_document import UnveillanceDocument
	from conf import DEBUG
	
	document = UnveillanceDocument(_id=task.doc_id)
	if document is None:
		print "DOC IS NONE"
		print "\n\n************** COMPILING METADATA [ERROR] ******************\n"
		return
	
	metadata = document.loadAsset(task.md_file)
	if metadata is None:
		print "NO METADATA FILE"
		print "\n\n************** COMPILING METADATA [ERROR] ******************\n"
		return
	
	import csv, re
	from Levenshtein import ratio
	from string import letters
	from vars import METADATA_ASPECTS, ASSET_TAGS
	
	numbers = str("".join([str(i) for i in range(0,10)]))
	missing_value = "NaN"
	
	labels = ["_id"]
	values = [document._id]
	
	try:
		for mda in METADATA_ASPECTS[task.md_namespace]:
			labels.append(mda['label'])
			pattern = re.compile(task.md_rx % (mda['tag_position'], mda['label']))
			if DEBUG: print pattern
			
			value = missing_value
			ideal = mda['ideal']
			
			if mda['ideal'] is None:
				if mda['type'] == "str":
					ideal = letters + numbers
				elif mda['type'] == "int":
					ideal = int(numbers)
			
			for line in metadata.splitlines():
				match = re.findall(pattern, line.strip())
				if len(match) == 1:
					if mda['type'] == "str":
						value = "%.9f" % ratio(ideal, str(match[0].replace("\"", '')))
					elif mda['type'] == "int":
						value = ideal/float(match[0].replace("\"", ''))
					break
					
			if value == missing_value:
				if mda['ideal'] is None: value = 1
				else: value = 0
			
			values.append(value)
		
		if hasattr(task, 'md_extras'):
			for key, value in task.md_extras.iteritems():
				labels.append(key)
				values.append(value)
		
		if DEBUG:
			print "labels %s" % labels
			print "values %s" % values
			
		from cStringIO import StringIO
		
		md_csv_file = StringIO()
		md_csv = csv.writer(md_csv_file, 
			delimter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

		md_csv.writerow(labels)
		md_csv.writerow(values)
		md_csv_file.close()
		
		document.addAsset(md_csv_file.getvalue(), "file_metadata.csv", 
			tags=[ASSET_TAGS["MD_F"]], 
			description="CSV representation of %s" % task.md_file)
			
		task.finish()
		print "\n\n************** COMPILING METADATA [END] ******************\n"
			
	except KeyError as e:
		if DEBUG: print e
		print "No metadata aspects for %s" % task.md_namespace
		print "\n\n************** COMPILING METADATA [ERROR] ******************\n"
		return