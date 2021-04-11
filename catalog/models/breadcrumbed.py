from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _

class BreadcrumbedObject():

    def get_parent_breadcrumbs(self):
        x= self.get_root_breadcrumbs()
        return x

    def get_breadcrumbs(self):
        breadcrumbs = self.get_parent_breadcrumbs()
        breadcrumbs.append((self.get_absolute_url(), self.__str__()))
        return breadcrumbs

    @staticmethod
    def get_root_breadcrumbs():
        return [(reverse('website:front'), _('Home page')),]


class Breadcrumbs(BreadcrumbedObject):

    def __init__(self, breadcrumbs:[list, tuple, str]):
        '''
        breadcrumbs [(url,title),...]
        '''
        self.breadcrumbs = self.get_root_breadcrumbs()
        self.append(breadcrumbs)

    def append(self, breadcrumbs:[list,tuple, str]):
        '''
        breadcrumbs [(url,title),...]
        '''

        print('breadcrumbs', breadcrumbs, type(breadcrumbs))
        print('self.breadcrumbs', self.breadcrumbs)

        if type(breadcrumbs) == list:
            self.breadcrumbs += breadcrumbs
        elif type(breadcrumbs) == tuple:
            self.breadcrumbs.append(breadcrumbs)
        else:
            self.breadcrumbs.append(('', str(breadcrumbs)))

        print('breadcrumbs', breadcrumbs, type(breadcrumbs))
        print('self.breadcrumbs', self.breadcrumbs)

    def get_breadcrumbs(self):
        return self.breadcrumbs