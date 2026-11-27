import json
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib import messages
from django.apps import apps

from store_admin.models import AdminAuditLog, TrashItem
from store_admin.utils import admin_required, role_required, log_audit

@admin_required
def audit_log_view(request):
    search_q = request.GET.get('q', '').strip()
    action_filter = request.GET.get('action', '')

    logs_qs = AdminAuditLog.objects.all().select_related('user')

    if search_q:
        logs_qs = logs_qs.filter(object_repr__icontains=search_q) | logs_qs.filter(changes_summary__icontains=search_q) | logs_qs.filter(user_email__icontains=search_q)

    if action_filter:
        logs_qs = logs_qs.filter(action=action_filter)

    paginator = Paginator(logs_qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'store_admin/audit/list.html', {
        'logs': page_obj,
        'search_q': search_q,
        'action_filter': action_filter,
        'active_nav': 'settings',
        'active_subnav': 'audit',
    })


@admin_required
def trash_bin_view(request):
    items = TrashItem.objects.all().order_by('-deleted_at')

    if request.method == 'POST':
        action = request.POST.get('action')
        trash_id = request.POST.get('trash_id')
        trash_item = get_object_or_404(TrashItem, id=trash_id)

        if action == 'restore':
            try:
                # Find the target model
                model_cls = apps.get_model('campaigns', trash_item.model_name) or apps.get_model('store_admin', trash_item.model_name)
                if model_cls:
                    obj = model_cls(**trash_item.serialized_data)
                    obj.save()
                    log_audit(request, 'restore', trash_item.model_name, obj.pk, trash_item.object_repr, "Restored from trash")
                    trash_item.delete()
                    messages.success(request, f"Restored '{trash_item.object_repr}' back to active catalog.")
            except Exception as e:
                messages.error(request, f"Error restoring item: {e}")
            return redirect('/admin/trash/')

        elif action == 'purge':
            obj_name = trash_item.object_repr
            trash_item.delete()
            log_audit(request, 'delete', trash_item.model_name, trash_item.object_id, obj_name, "Permanently purged from trash")
            messages.success(request, f"Permanently deleted '{obj_name}'.")
            return redirect('/admin/trash/')

    return render(request, 'store_admin/audit/trash.html', {
        'items': items,
        'active_nav': 'settings',
        'active_subnav': 'trash',
    })
