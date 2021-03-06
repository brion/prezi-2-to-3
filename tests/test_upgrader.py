import unittest
import json

from iiif_prezi_upgrader import prezi_upgrader

###
### Basic Manifest Tests
###

class TestManifest(unittest.TestCase):
	
	def setUp(self):
		flags= {"ext_ok": False, "deref_links": False}
		self.upgrader = prezi_upgrader.Upgrader(flags)
		self.results = self.upgrader.process_cached('tests/input_data/manifest-basic.json')

	def test_context(self):
		newctxt = ["http://www.w3.org/ns/anno.jsonld",
			"http://iiif.io/api/presentation/3/context.json"]
		self.assertTrue('@context' in self.results)
		self.assertEqual(self.results['@context'], newctxt)

	def test_items(self):
		self.assertTrue('items' in self.results)
		self.assertTrue('items' in self.results['items'][0])
		self.assertTrue('items' in self.results['items'][0]['items'][0])
		self.assertTrue('items' in self.results['structures'][0])
		self.assertTrue('items' in self.results['structures'][0]['items'][1])

	def test_id(self):
		self.assertTrue('id' in self.results)
		self.assertEqual(self.results['id'], \
			"http://iiif.io/api/presentation/2.1/example/fixtures/1/manifest.json")
		self.assertTrue('id' in self.results['structures'][0])
		self.assertTrue('id' in self.results['items'][0]['items'][0])

	def test_type(self):
		# Also tests values of type
		self.assertTrue('type' in self.results)
		self.assertEqual(self.results['type'], "Manifest")
		self.assertTrue('type' in self.results['items'][0])
		self.assertEqual(self.results['items'][0]['type'], 'Sequence')
		cvs = self.results['items'][0]['items'][0]
		self.assertEqual(cvs['type'], 'Canvas')
		self.assertEqual(cvs['items'][0]['type'], "AnnotationPage")
		self.assertEqual(cvs['items'][0]['items'][0]['type'], "Annotation")

	def test_startCanvas(self):
		cvs = "http://iiif.io/api/presentation/2.1/example/fixtures/canvas/1/c1.json"
		self.assertTrue('start' in self.results)
		self.assertEqual(self.results['start']['id'], cvs)
		self.assertTrue('start' in self.results['items'][0])
		self.assertEqual(self.results['items'][0]['start']['id'], cvs)
		self.assertEqual(self.results['start']['type'], 'Canvas')

	def test_license(self):
		lic = "http://iiif.io/event/conduct/"
		self.assertTrue('rights' in self.results)
		self.assertEqual(self.results['rights'][0]['id'], lic)

	def test_viewingHint(self):
		self.assertTrue('behavior' in self.results)
		self.assertEqual(self.results['behavior'], ["paged"])
		self.assertTrue('behavior' in self.results['items'][0])
		self.assertEqual(self.results['items'][0]['behavior'], ["paged"])


	def test_arrays(self):
		self.assertEqual(type(self.results['behavior']), list)
		self.assertEqual(type(self.results['logo']), list)
		self.assertEqual(type(self.results['seeAlso']), list)

	def test_uri_string(self):
		self.assertEqual(type(self.results['rendering'][0]), dict)
		self.assertEqual(type(self.results['rights'][0]), dict)
		self.assertEqual(type(self.results['start']), dict)

	def test_languagemap(self):
		self.assertEqual(type(self.results['label']), dict)
		self.assertTrue('@none' in self.results['label'])
		self.assertEqual(self.results['label']['@none'], ["Manifest Label"])
		self.assertTrue('metadata' in self.results)
		md = self.results['metadata']
		self.assertEqual(type(md[0]['label']), dict)
		self.assertEqual(type(md[0]['label']['@none']), list)
		self.assertEqual(md[0]['label']['@none'][0], "MD Label 1")
		self.assertEqual(type(md[0]['value']), dict)		
		self.assertEqual(type(md[0]['value']['@none']), list)
		self.assertEqual(md[0]['value']['@none'][0], "MD Value 1")

		# md[1] has two values 
		self.assertEqual(len(md[1]['value']['@none']), 2)
		# md[2] has en and fr values
		self.assertTrue('en' in md[2]['value'])
		self.assertTrue('fr' in md[2]['value'])

	def test_description(self):
		if self.upgrader.description_is_metadata:
			# look in metadata
			found = 0
			for md in self.results['metadata']:
				if md['label']['@none'][0] == "Description":
					found = 1
					self.assertEqual(md['value']['@none'][0], 
						"This is a description of the Manifest")					
			# ensure it was generated 
			self.assertEqual(found, 1)
		else:
			# look in summary
			self.assertTrue('summary' in self.results)
			self.assertEqual(type(self.results['summary']), dict)
			self.assertTrue('@none' in self.results['summary'])
			self.assertEqual(self.results['summary']['@none'][0], 
				"This is a description of the Manifest")

	def test_ranges(self):
		ranges = self.results['structures']
		self.assertEqual(len(ranges), 1)
		rng = ranges[0]
		# print(json.dumps(rng, indent=2, sort_keys=True))		
		self.assertTrue(not "behavior" in rng)
		self.assertEqual(rng['type'], "Range")
		self.assertTrue("items" in rng)
		self.assertEqual(len(rng['items']), 3)
		# [0] is a Canvas
		self.assertTrue("items" in rng['items'][1])
		self.assertTrue("items" in rng['items'][1]['items'][0])
		self.assertTrue("items" in rng['items'][2])



###
### Annotation Tests
###

class TestAnnotations(unittest.TestCase):

	def setUp(self):
		flags= {"ext_ok": False, "deref_links": False}
		self.upgrader = prezi_upgrader.Upgrader(flags)
		self.results = self.upgrader.process_cached('tests/input_data/manifest-annos.json')
		self.annotations = self.results['items'][0]['items'][0]['items'][0]['items']

	def test_body(self):
		anno = self.annotations[0]
		self.assertTrue('body' in anno)
		self.assertEqual(anno['body']['id'], 
			"http://iiif.io/api/presentation/2.1/example/fixtures/resources/page1-full.png")

	def test_target(self):
		anno = self.annotations[0]
		self.assertTrue('target' in anno)
		self.assertEqual(anno['target'],
		"http://iiif.io/api/presentation/2.1/example/fixtures/canvas/1/c1.json")

	def test_type(self):
		anno = self.annotations[0]
		self.assertTrue('type' in anno)
		self.assertEqual(anno['type'], "Annotation")

	def test_motivation(self):
		anno = self.annotations[0]
		self.assertTrue('motivation' in anno)
		self.assertEqual(anno['motivation'], "painting")

	def test_source(self):
		anno = self.annotations[1]
		self.assertEqual(anno['body']['type'], 'SpecificResource')
		self.assertTrue('source' in anno['body'])

	def test_ContentAsText(self):
		anno = self.annotations[2]
		self.assertEqual(anno['body']['type'], 'TextualBody')
		self.assertTrue('value' in anno['body'])

	def test_choice(self):
		anno = self.annotations[3]
		self.assertEqual(anno['body']['type'], 'Choice')
		self.assertTrue('items' in anno['body'])
		self.assertEqual(len(anno['body']['items']), 2)

	def test_style(self):
		anno = self.annotations[4]
		# print(json.dumps(anno, indent=2, sort_keys=True))
		self.assertTrue('stylesheet' in anno)
		self.assertEqual(anno['stylesheet']['type'], "CssStylesheet")
		self.assertTrue("value" in anno['stylesheet'])
		self.assertEqual(anno['stylesheet']['value'], ".red {color: red;}")
		self.assertTrue("styleClass" in anno['body'])
		self.assertEqual(anno['body']['styleClass'], "red")


###
### Service Tests
###



class TestServices(unittest.TestCase):

	def setUp(self):
		flags= {"ext_ok": False, "deref_links": False}
		self.upgrader = prezi_upgrader.Upgrader(flags)
		self.results = self.upgrader.process_cached('tests/input_data/manifest-services.json')

	def test_search(self):
		# Search and Autocomplete are on the Manifest
		manifest = self.results
		self.assertTrue('service' in manifest)
		self.assertEqual(type(manifest['service']), list)
		svc = manifest['service'][0]
		self.assertTrue(not '@context' in svc)
		self.assertEqual(svc['id'], "http://example.org/services/identifier/search")
		self.assertEqual(svc['type'], "SearchService1")
		self.assertTrue('service' in svc)
		self.assertEqual(svc['service'][0]['type'], "AutoCompleteService1")

	def test_image(self):
		svc = self.results['items'][0]['items'][0]['items'][0]['items'][0]['body']['service'][0]
		self.assertTrue('id' in svc)
		self.assertTrue('type' in svc)
		self.assertEqual(svc['type'], "ImageService2")
		self.assertTrue('profile' in svc)
		self.assertEqual(svc['profile'], 'level1')

	def test_auth(self):
		svc = self.results['items'][0]['items'][0]['items'][0]['items'][0]['body']['service'][0]['service'][0]
		self.assertTrue('id' in svc)
		self.assertTrue('type' in svc)
		self.assertEqual(svc['type'], "AuthCookieService1")
		self.assertTrue('profile' in svc)
		self.assertEqual(svc['profile'], 'login')
		self.assertTrue('service' in svc)
		token = svc['service'][0]
		self.assertTrue('id' in token)
		self.assertTrue('type' in token)
		self.assertEqual(token['type'], "AuthTokenService1")
		logout = svc['service'][1]
		self.assertTrue('id' in logout)
		self.assertTrue('type' in logout)
		self.assertEqual(logout['type'], "AuthLogoutService1")


###
### Collection Tests
###

class TestCollection(unittest.TestCase):

	def setUp(self):
		flags= {"ext_ok": False, "deref_links": False}
		self.upgrader = prezi_upgrader.Upgrader(flags)
		self.results = self.upgrader.process_cached('tests/input_data/collection-basic.json')

	def test_items(self):
		self.assertTrue('items' in self.results)
		items = self.results['items']
		# print(json.dumps(items, indent=2, sort_keys=True))
		# Two Collections, then One Manifest
		self.assertEqual(len(items), 3)
		self.assertEqual(items[0]['type'], "Collection")
		self.assertEqual(items[2]['type'], "Manifest")
		self.assertTrue('items' in items[0])
		# Three Members: Collection, Manifest, Collection
		items2 = items[0]['items']
		self.assertEqual(len(items2), 3)
		self.assertEqual(items2[0]['type'], "Collection")
		self.assertEqual(items2[1]['type'], "Manifest")
		self.assertTrue('behavior' in items2[0])
		self.assertTrue('multi-part' in items2[0]['behavior'])

class TestRemote(unittest.TestCase):

	def test_remotes(self):
		uris = [
			"https://api.bl.uk/metadata/iiif/ark:/81055/vdc_100054149545.0x000001/manifest.json",
			"https://d.lib.ncsu.edu/collections/catalog/nubian-message-1992-11-30/manifest",
			"https://sinai-images.library.ucla.edu/iiif/ark%3A%252F21198%252Fz1bc4wfw/manifest"
		]
		
		for u in uris:
			flags = {"deref_links": False}
			up = prezi_upgrader.Upgrader(flags)
			res = up.process_uri(u)
