from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    url(r'^$', 'quentomu.views.home', name='home'),
    url(r'^conversations$', 'quentomu.views.conversation', name='conversation'),
    url(r'^topics$', 'quentomu.views.topics', name='topics'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    #pols
    url(r'^testDN/', 'quentomu.views.DeliveryNotif',name = 'DelivNotif'),
    url(r'^testInbox/', 'quentomu.views.RecievedMsgs',name = 'RecieveMsgs'),
    url(r'^testSendMoney/',name = 'Remittance'),
]
