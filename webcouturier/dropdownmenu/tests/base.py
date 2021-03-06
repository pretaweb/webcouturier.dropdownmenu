"""Test setup for integration and functional tests.

When we import PloneTestCase and then call setupPloneSite(), all of Plone's
products are loaded, and a Plone site will be created. This happens at module
level, which makes it faster to run each test, but slows down test runner
startup.
"""

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

#
# When ZopeTestCase configures Zope, it will *not* auto-load products in
# Products/. Instead, we have to use a statement such as:
#
#   ztc.installProduct('SimpleAttachment')
#
# This does *not* apply to products in eggs and Python packages (i.e. not in
# the Products.*) namespace. For that, see below.
#
# All of Plone's products are already set up by PloneTestCase.
#


@onsetup
def setup_product():
    """Set up the package and its dependencies.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer. We could have created our
    own layer, but this is the easiest way for Plone integration tests.
    """

    # Load the ZCML configuration for the example.tests package.
    # This can of course use <include /> to include other packages.

    fiveconfigure.debug_mode = True
    import webcouturier.dropdownmenu
    zcml.load_config('configure.zcml', webcouturier.dropdownmenu)
    fiveconfigure.debug_mode = False

    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML. Thus, we do it here. Note the use of installPackage() instead
    # of installProduct().
    #
    # This is *only* necessary for packages outside the Products.* namespace
    # which are also declared as Zope 2 products, using
    # <five:registerPackage /> in ZCML.

    # We may also need to load dependencies, e.g.:
    #
    #   ztc.installPackage('borg.localrole')
    #

    ztc.installPackage('webcouturier.dropdownmenu')

# The order here is important: We first call the (deferred) function which
# installs the products we need for this product. Then, we let PloneTestCase
# set up this product on installation.

setup_product()
ptc.setupPloneSite(products=['webcouturier.dropdownmenu'])


class DropdownsTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here. This applies to unit
    test cases.
    """


class DropdownsFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use doctest
    syntax. Again, we can put basic common utility or setup code in here.

    In this case, we set up some folders, sub folder, and sub sub
    folders to have a reasonably interesting test environment.
    """

    def setUp(self):
        super(DropdownsFunctionalTestCase, self).setUp()
        self.loginAsPortalOwner()
        wf_tool = self.portal.portal_workflow
        root_folders_ids = []
        for i in range(2):
            folder_id = 'folder-%s' % i
            self.portal.invokeFactory('Folder', folder_id)
            wf_tool.doActionFor(getattr(self.portal, folder_id), 'publish')
            root_folders_ids.append(folder_id)

        # now we add some subfolders to one of the folders
        folder_one = getattr(self.portal, 'folder-0')
        for i in range(2):
            folder_id = 'sub-%s' % i
            folder_one.invokeFactory('Folder', folder_id)
            wf_tool.doActionFor(getattr(folder_one, folder_id), 'publish')

        # And some sub-sub folders
        subfolder = getattr(folder_one, 'sub-0')
        for i in range(2):
            folder_id = 'sub-sub-%s' % i
            subfolder.invokeFactory('Folder', folder_id)
            wf_tool.doActionFor(getattr(subfolder, folder_id), 'publish')

        self.logout()
