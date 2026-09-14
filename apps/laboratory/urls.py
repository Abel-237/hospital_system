from django.urls import path
from .views import (
    LabOrderListView, LabOrderCreateView, LabOrderDetailView,
    LabResultUpdateView, LabReportPDFView
)

app_name = 'laboratory'

urlpatterns = [
    path('', LabOrderListView.as_view(), name='order_list'),
    path('order/create/', LabOrderCreateView.as_view(), name='order_create'),
    path('order/<int:pk>/', LabOrderDetailView.as_view(), name='order_detail'),
    path('item/<int:item_id>/result/', LabResultUpdateView.as_view(), name='result_update'),
    path('order/<int:pk>/pdf/', LabReportPDFView.as_view(), name='report_pdf'),
]
