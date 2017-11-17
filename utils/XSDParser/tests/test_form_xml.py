from selenium import webdriver
import time
from mgi.tests import SeleniumTestCase

from mgi.common import update_dependencies
from mgi.settings import BASE_DIR
from os.path import join
from os import listdir, remove

from mgi.models import create_template, TemplateVersion
from lxml import etree
from mgi.tests import are_equals
from pymongo import MongoClient
from mgi.settings import MONGODB_URI
from pymongo.errors import OperationFailure

RESOURCES_PATH = join(BASE_DIR, 'utils', 'XSDParser', 'tests', 'data', 'parser', 'schema', 'namespace')
USER = "admin"
PASSWORD = "admin"
BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 5


def clean_db():
    # create a connection
    client = MongoClient(MONGODB_URI)
    # connect to the db 'mgi'
    db = client['mgi_test']
    # clear all collections
    for collection in db.collection_names():
        try:
            if collection != 'system.indexes':
                db.drop_collection(collection)
        except OperationFailure:
            pass


def login(driver, base_url, user, password):
    driver.get("{0}/{1}".format(base_url, "login"))
    driver.find_element_by_id("id_username").clear()
    driver.find_element_by_id("id_username").send_keys(user)
    driver.find_element_by_id("id_password").clear()
    driver.find_element_by_id("id_password").send_keys(password)
    driver.find_element_by_css_selector("button.btn").click()
    time.sleep(TIMEOUT)


def load_new_form(driver, base_url, form_name):
    driver.get("{0}/{1}".format(base_url, "curate"))
    driver.find_element_by_css_selector("button.btn.set-template").click()
    time.sleep(TIMEOUT)
    driver.find_element_by_name("curate_form").click()
    driver.find_element_by_id("id_document_name").clear()
    driver.find_element_by_id("id_document_name").send_keys(form_name)
    time.sleep(TIMEOUT)
    driver.find_element_by_xpath("(//button[@type='button'])[2]").click()


class LoadFormToXML(SeleniumTestCase):
    """
    """
    def setUp(self):
        # clean mongo db collections
        clean_db()

        self.resources_path = join(RESOURCES_PATH, 'element')
        self.results_path = join(RESOURCES_PATH, 'results_element')

        try:
            # remove all result files if there are some
            for filename in listdir(self.results_path):
                remove(join(self.results_path, filename))
        except:
            pass

        # setup Selenium

        # define profile for custom download
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir', self.results_path)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/xml')

        # define Firefox web driver
        self.driver = webdriver.Firefox(profile)
        self.driver.implicitly_wait(10)
        self.base_url = BASE_URL
        self.verificationErrors = []
        self.accept_next_alert = True

        # login to MDCS
        login(self.driver, self.base_url, USER, PASSWORD)

    def test(self):
        print "***************"
        print "Elements Tests:"
        errors = []
        try:
            # get all the files in the directory
            for filename in listdir(self.resources_path):
                # clean mongo db collections
                clean_db()
                if filename.endswith('.xsd'):
                    # print 'TESTING: {}'.format(filename)
                    file_id = filename.split('.')[0]
                    try:
                        self.execute_test(file_id)
                    except Exception, e:
                        print '{} FAILED'.format(filename)
                        print e
                        errors.append(str(e.message))

        except Exception, e:
            errors.append(str(e.message))

        if len(errors) > 0:
            self.fail()

    def execute_test(self, file_id):
        filename = '{}.xsd'.format(file_id)

        # load XSD
        xsd_file_path = join(self.resources_path, filename)
        xsd_file = open(xsd_file_path, 'r')
        xsd_file_content = xsd_file.read()

        # create template
        template = create_template(xsd_file_content, filename, filename)

        # load the form
        load_new_form(self.driver, self.base_url, file_id)
        time.sleep(TIMEOUT)
        # download XML
        self.driver.execute_script("downloadCurrentXML();")

        # wait a bit more to let time to save the file
        time.sleep(TIMEOUT * 5)

        # load expected result
        exp_result_path = join(self.resources_path, "{0}.xml".format(file_id))
        exp_result_file = open(exp_result_path, 'r')
        exp_result_content = exp_result_file.read()

        # load result generated by the form
        result_path = join(self.results_path, "{0}.xml".format(file_id))
        result_file = open(result_path, 'r')
        result_content = result_file.read()

        expected = etree.fromstring(exp_result_content)
        result = etree.fromstring(result_content)

        if not are_equals(expected, result):
            raise Exception('NOT EQUALS TO EXPECTED: {}'.format(file_id))

    def tearDown(self):
        # clean all collections in db
        clean_db()
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
        time.sleep(TIMEOUT)


class LoadFormIncludeToXML(SeleniumTestCase):
    """
    """
    def setUp(self):
        # clean mongo db collections
        clean_db()

        self.resources_path = join(RESOURCES_PATH, 'include')
        self.results_path = join(RESOURCES_PATH, 'results_include')

        try:
            # remove all result files if there are some
            for filename in listdir(self.results_path):
                remove(join(self.results_path, filename))
        except:
            pass

        # setup Selenium

        # define profile for custom download
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir', self.results_path)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/xml')

        # define Firefox web driver
        self.driver = webdriver.Firefox(profile)
        self.driver.implicitly_wait(30)
        self.base_url = BASE_URL
        self.verificationErrors = []
        self.accept_next_alert = True
        # login to MDCS
        login(self.driver, self.base_url, USER, PASSWORD)

    def test(self):
        print "***************"
        print "Includes Tests:"
        errors = []
        try:
            # get all the files in the directory
            for filename in listdir(self.resources_path):
                # clean mongo db collections
                clean_db()
                if filename.endswith('.xsd') and 'inc' not in filename:
                    # print 'TESTING: {}'.format(filename)
                    file_id = filename.split('.')[0]
                    try:
                        self.execute_test(file_id)
                    except Exception, e:
                        print '{} FAILED'.format(filename)
                        print e.message
                        errors.append(str(e.message))

        except Exception, e:
            errors.append(str(e.message))

        if len(errors) > 0:
            self.fail()

    def execute_test(self, file_id):
        filename_inc = '{}_inc.xsd'.format(file_id)

        # load XSD
        xsd_file_path_inc = join(self.resources_path, filename_inc)
        xsd_file_inc = open(xsd_file_path_inc, 'r')
        xsd_file_content_inc = xsd_file_inc.read()

        # create template
        template_inc = create_template(xsd_file_content_inc, filename_inc, filename_inc)
        template_version = TemplateVersion.objects().get(pk=template_inc.templateVersion)
        # remove the dependency template
        template_version.deletedVersions.append(str(template_inc.id))
        template_version.isDeleted = True
        template_version.save()

        filename = '{}.xsd'.format(file_id)

        # load XSD
        xsd_file_path = join(self.resources_path, filename)
        xsd_file = open(xsd_file_path, 'r')
        xsd_file_content = xsd_file.read()

        # create template
        xsd_tree = etree.fromstring(xsd_file_content)
        update_dependencies(xsd_tree, {filename_inc: str(template_inc.id)})
        xsd_file_content = etree.tostring(xsd_tree)

        template = create_template(xsd_file_content, filename, filename, [str(template_inc.id)])

        # load the form
        load_new_form(self.driver, self.base_url, file_id)
        time.sleep(TIMEOUT)
        # download XML
        self.driver.execute_script("downloadCurrentXML();")

        # wait a bit more to let time to save the file
        time.sleep(TIMEOUT * 5)

        # load expected result
        exp_result_path = join(self.resources_path, "{0}.xml".format(file_id))
        exp_result_file = open(exp_result_path, 'r')
        exp_result_content = exp_result_file.read()

        # load result generated by the form
        result_path = join(self.results_path, "{0}.xml".format(file_id))
        result_file = open(result_path, 'r')
        result_content = result_file.read()

        expected = etree.fromstring(exp_result_content)
        result = etree.fromstring(result_content)

        if not are_equals(expected, result):
            raise Exception('NOT EQUALS TO EXPECTED: {}'.format(file_id))

    def tearDown(self):
        # clean all collections in db
        clean_db()
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
        time.sleep(TIMEOUT)


class LoadFormImportToXML(SeleniumTestCase):
    """
    """
    def setUp(self):
        # clean mongo db collections
        clean_db()

        self.resources_path = join(RESOURCES_PATH, 'import')
        self.results_path = join(RESOURCES_PATH, 'results_imports')

        try:
            # remove all result files if there are some
            for filename in listdir(self.results_path):
                remove(join(self.results_path, filename))
        except:
            pass

        # setup Selenium

        # define profile for custom download
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir', self.results_path)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/xml')

        # define Firefox web driver
        self.driver = webdriver.Firefox(profile)
        self.driver.implicitly_wait(30)
        self.base_url = BASE_URL
        self.verificationErrors = []
        self.accept_next_alert = True
        # login to MDCS
        login(self.driver, self.base_url, USER, PASSWORD)

    def test(self):
        print "***************"
        print "Imports Tests:"
        errors = []
        try:
            # get all the files in the directory
            for filename in listdir(self.resources_path):
                # clean mongo db collections
                clean_db()
                if filename.endswith('.xsd') and 'inc' not in filename:
                    # print 'TESTING: {}'.format(filename)
                    file_id = filename.split('.')[0]
                    try:
                        self.execute_test(file_id)
                    except Exception, e:
                        print '{} FAILED'.format(filename)
                        print e.message
                        errors.append(str(e.message))

        except Exception, e:
            errors.append(str(e.message))

        if len(errors) > 0:
            self.fail()

    def execute_test(self, file_id):
        filename_inc = '{}_inc.xsd'.format(file_id)

        # load XSD
        xsd_file_path_inc = join(self.resources_path, filename_inc)
        xsd_file_inc = open(xsd_file_path_inc, 'r')
        xsd_file_content_inc = xsd_file_inc.read()

        # create template
        template_inc = create_template(xsd_file_content_inc, filename_inc, filename_inc)
        template_version = TemplateVersion.objects().get(pk=template_inc.templateVersion)
        # remove the dependency template
        template_version.deletedVersions.append(str(template_inc.id))
        template_version.isDeleted = True
        template_version.save()

        filename = '{}.xsd'.format(file_id)

        # load XSD
        xsd_file_path = join(self.resources_path, filename)
        xsd_file = open(xsd_file_path, 'r')
        xsd_file_content = xsd_file.read()

        # create template
        xsd_tree = etree.fromstring(xsd_file_content)
        update_dependencies(xsd_tree, {filename_inc: str(template_inc.id)})
        xsd_file_content = etree.tostring(xsd_tree)

        template = create_template(xsd_file_content, filename, filename, [str(template_inc.id)])

        # load the form
        load_new_form(self.driver, self.base_url, file_id)
        time.sleep(TIMEOUT)
        # download XML
        self.driver.execute_script("downloadCurrentXML();")

        # wait a bit more to let time to save the file
        time.sleep(TIMEOUT * 5)

        # load expected result
        exp_result_path = join(self.resources_path, "{0}.xml".format(file_id))
        exp_result_file = open(exp_result_path, 'r')
        exp_result_content = exp_result_file.read()

        # load result generated by the form
        result_path = join(self.results_path, "{0}.xml".format(file_id))
        result_file = open(result_path, 'r')
        result_content = result_file.read()

        expected = etree.fromstring(exp_result_content)
        result = etree.fromstring(result_content)

        if not are_equals(expected, result):
            raise Exception('NOT EQUALS TO EXPECTED: {}'.format(file_id))

    def tearDown(self):
        # clean all collections in db
        clean_db()
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
        time.sleep(TIMEOUT)