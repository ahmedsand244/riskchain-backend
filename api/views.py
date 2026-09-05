import json
import os
import random
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Shipment, Notification
from django.db.models import Count, Avg
import csv
import io

from django.conf import settings

def login_page(request):
    """Serve the login page"""
    if request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('/')
    return render(request, 'login.html')

def dashboard(request):
    """Serve the React + Tailwind CDN frontend — requires auth"""
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('/login/')
    return render(request, 'index.html')

@csrf_exempt
def predict_risk(request):
    """
    API endpoint that accepts JSON shipment telemetry and returns 
    a risk prediction and a prescriptive mitigation string.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            risk_probability = 0.0
            prediction_label = "ON-TIME"
            
            try:
                import joblib
                import pandas as pd

                # Load the real pipeline model dynamically
                model_path = os.path.join(settings.BASE_DIR, 'late_delivery_model.pkl')
                if not os.path.exists(model_path):
                    # fallback to parent directory or legacy path if exists
                    parent_path = os.path.join(settings.BASE_DIR.parent, 'late_delivery_model.pkl')
                    if os.path.exists(parent_path):
                        model_path = parent_path
                
                if os.path.exists(model_path):
                    model = joblib.load(model_path)
                    
                    # Expected features
                    features = [
                        'Days for shipment (scheduled)', 'Benefit per order', 'Sales per customer',
                        'Order Item Discount', 'Order Item Quantity', 'Product Price', 'order_hour',
                        'ship_hour', 'ship_day_of_week', 'order_day_of_week', 'is_weekend',
                        'Type_CASH', 'Type_DEBIT', 'Type_PAYMENT', 'Type_TRANSFER',
                        'Customer Segment_Consumer', 'Customer Segment_Corporate',
                        'Customer Segment_Home Office', 'Shipping Mode_First Class',
                        'Shipping Mode_Same Day', 'Shipping Mode_Second Class',
                        'Shipping Mode_Standard Class', 'Customer City_Caguas', 'Customer State_CA',
                        'Customer State_NY', 'Customer State_PR', 'Order Region_Central America',
                        'Order Region_Northern Europe', 'Order Region_Oceania',
                        'Order Region_South America', 'Order Region_Western Europe',
                        'Market_Africa', 'Market_Europe', 'Market_LATAM', 'Market_Pacific Asia',
                        'Market_USCA'
                    ]
                    
                    # Initialize a zeroed dictionary
                    input_dict = {f: 0 for f in features}
                    
                    # Map numerical inputs
                    input_dict['Days for shipment (scheduled)'] = data.get('scheduled_days', 3)
                    input_dict['Benefit per order'] = data.get('benefit_per_order', 20)
                    input_dict['Sales per customer'] = data.get('sales_per_customer', 200)
                    input_dict['Order Item Discount'] = data.get('order_item_discount', 10)
                    input_dict['Order Item Quantity'] = data.get('order_item_quantity', 1)
                    input_dict['Product Price'] = data.get('product_price', 150)
                    input_dict['order_hour'] = data.get('order_hour', 10)
                    input_dict['ship_hour'] = (data.get('order_hour', 10) + data.get('actual_duration', 3)) % 24
                    input_dict['ship_day_of_week'] = (data.get('order_day_of_week', 2) + data.get('actual_duration', 3)) % 7
                    input_dict['order_day_of_week'] = data.get('order_day_of_week', 2)
                    input_dict['is_weekend'] = 1 if data.get('order_day_of_week', 2) >= 5 else 0
                    
                    # Map categorical inputs (One-Hot Encoded)
                    type_val = f"Type_{data.get('type', 'DEBIT')}"
                    if type_val in input_dict: input_dict[type_val] = 1
                        
                    seg_val = f"Customer Segment_{data.get('customer_segment', 'Consumer')}"
                    if seg_val in input_dict: input_dict[seg_val] = 1
                        
                    mode_val = f"Shipping Mode_{data.get('shipping_mode', 'Standard Class')}"
                    if mode_val in input_dict: input_dict[mode_val] = 1
                        
                    region_val = f"Order Region_{data.get('order_region', 'Western Europe')}"
                    if region_val in input_dict: input_dict[region_val] = 1
                        
                    market_val = f"Market_{data.get('market', 'Europe')}"
                    if market_val in input_dict: input_dict[market_val] = 1
                    
                    # Default City/State 
                    input_dict['Customer City_Caguas'] = 1
                    input_dict['Customer State_PR'] = 1
                    
                    # Create DataFrame
                    df = pd.DataFrame([input_dict])
                    
                    # Predict!
                    pred_class = model.predict(df)[0]
                    prob = model.predict_proba(df)[0]
                    
                    risk_probability = float(prob[1]) # Probability of class 1 (Late/Risk)
                    
                else:
                    raise FileNotFoundError("Model files not found. Simulating output.")
                    
            except Exception as e:
                # -----------------
                # MOCK / SIMULATION LOGIC (To ensure dashboard visualizes properly)
                # -----------------
                base_risk = 0.1
                
                # Add risk if shipping mode is standard and region is difficult
                if data.get("shipping_mode") == "Standard Class":
                    base_risk += 0.2
                if data.get("actual_duration", 0) > data.get("scheduled_days", 0):
                    base_risk += 0.4
                if data.get("order_day_of_week", 0) >= 5: # Weekend
                    base_risk += 0.15
                    
                risk_probability = min(0.99, base_risk + random.uniform(-0.05, 0.1))
            
            # Prescriptive Logic Generation
            if risk_probability > 0.5:
                prediction_label = "LATE"
                
                # Generate dynamic prescriptive text
                if data.get("actual_duration", 0) > data.get("scheduled_days", 0):
                    en_msg = "⚠️ Immediate Action Required: Shipment exceeding scheduled days. Upgrade to expedited shipping carrier."
                    ar_msg = "⚠️ إجراء فوري مطلوب: الشحنة تتجاوز الأيام المجدولة. يرجى الترقية إلى شركة شحن سريع."
                elif data.get("shipping_mode") == "Standard Class":
                    en_msg = "⚠️ High Delay Probability detected for Standard Class in this region. Reroute via Air Freight."
                    ar_msg = "⚠️ احتمال تأخير عالي لوحظ في الشحن العادي في هذه المنطقة. يرجى إعادة التوجيه عبر الشحن الجوي."
                else:
                    en_msg = "⚠️ Supply Chain bottleneck detected. Inform local warehouse to prepare contingency stock."
                    ar_msg = "⚠️ تم رصد اختناق في سلسلة التوريد. يرجى إبلاغ المستودع المحلي لتجهيز مخزون الطوارئ."
            else:
                prediction_label = "ON-TIME"
                en_msg = "✅ Shipment telemetry nominal. Current logistics route is optimal. No action required."
                ar_msg = "✅ بيانات الشحنة طبيعية. المسار اللوجستي الحالي مثالي. لا يتطلب أي إجراء."
                
            # Save to Database
            shipment_obj = None
            if request.user.is_authenticated:
                shipment_obj = Shipment.objects.create(
                    user=request.user,
                    shipping_mode=data.get('shipping_mode', 'Standard Class'),
                    order_region=data.get('order_region', 'Western Europe'),
                    market=data.get('market', 'Europe'),
                    transaction_type=data.get('type', 'DEBIT'),
                    customer_segment=data.get('customer_segment', 'Consumer'),
                    scheduled_days=data.get('scheduled_days', 3),
                    actual_duration=data.get('actual_duration', 3),
                    order_hour=data.get('order_hour', 10),
                    order_day_of_week=data.get('order_day_of_week', 2),
                    predicted_risk=risk_probability,
                    predicted_class=prediction_label,
                    actual_status='PENDING'
                )

                if risk_probability > 0.60:
                    # Create Notification
                    managers = User.objects.filter(is_staff=True)
                    for manager in managers:
                        Notification.objects.create(
                            user=manager,
                            message_en=f"High Risk Alert ({(risk_probability*100):.1f}%) for shipment to {shipment_obj.order_region}.",
                            message_ar=f"تنبيه خطورة عالية ({(risk_probability*100):.1f}%) لشحنة متجهة إلى {shipment_obj.order_region}.",
                            shipment=shipment_obj
                        )
                
            return JsonResponse({
                "status": "success",
                "prediction": prediction_label,
                "risk_probability": risk_probability,
                "mitigation_en": en_msg,
                "mitigation_ar": ar_msg,
                "input_echo": data
            })
            
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)
    
    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

def auth_status(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "is_authenticated": True,
            "user": {
                "username": request.user.username,
                "email": request.user.email
            }
        })
    return JsonResponse({"is_authenticated": False})

def google_login_dispatcher(request):
    """
    Dispatcher for Google Login:
    - If a valid custom GOOGLE_CLIENT_ID is configured, redirect to allauth Google OAuth.
    - Otherwise (or if ?mode=demo is requested), log in directly as Google Agent.
    """
    from django.shortcuts import redirect
    from django.conf import settings
    
    client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '').strip()
    has_real_id = bool(client_id and not client_id.startswith('riskchain-') and not client_id.startswith('your-'))
    
    if has_real_id and request.GET.get('mode') != 'demo':
        return redirect('/accounts/google/login/')
    
    # Create or get Google demo user
    user, _ = User.objects.get_or_create(
        email='google.agent@riskchain.ai',
        defaults={
            'username': 'google_agent',
            'first_name': 'Google Agent',
            'is_active': True
        }
    )
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return redirect('/')

@csrf_exempt
def auth_login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")
            # For prototype simplicity, lookup user by email, authenticate by username
            user_obj = User.objects.filter(email=email).first()
            if not user_obj:
                return JsonResponse({"status": "error", "message": "Invalid credentials"}, status=400)
                
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse({"status": "error", "message": "Invalid credentials"}, status=400)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

@csrf_exempt
def auth_register(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            password = data.get("password", "")
            if not email or not password:
                return JsonResponse({"status": "error", "message": "Email and password required"}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({"status": "error", "message": "Email already registered"}, status=400)
            username = email.split('@')[0]
            # ensure unique username
            base = username
            i = 1
            while User.objects.filter(username=username).exists():
                username = f"{base}{i}"; i += 1
            first = name.split()[0] if name else username
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first)
            login(request, user)
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

@csrf_exempt
def auth_logout(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

@csrf_exempt
def get_dashboard_stats(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)
    
    qs = Shipment.objects.all() if request.user.is_staff else Shipment.objects.filter(user=request.user)
    
    total = qs.count()
    late = qs.filter(predicted_class="LATE").count()
    on_time = total - late
    avg_risk = qs.aggregate(Avg('predicted_risk'))['predicted_risk__avg'] or 0
    
    regions = qs.values('order_region').annotate(total=Count('id')).order_by('-total')[:5]
    region_data = [{"region": r['order_region'], "count": r['total']} for r in regions]

    # New Data for Pie and Bar Charts
    pie_data = [
        {"name": "On-Time", "value": on_time},
        {"name": "Late", "value": late}
    ]
    
    shipping_modes = qs.values('shipping_mode').annotate(avg_risk=Avg('predicted_risk'), count=Count('id')).order_by('-avg_risk')[:5]
    shipping_mode_data = [{"mode": sm['shipping_mode'], "risk": (sm['avg_risk'] or 0) * 100, "count": sm['count']} for sm in shipping_modes]

    return JsonResponse({
        "status": "success",
        "total": total,
        "late": late,
        "on_time": on_time,
        "avg_risk": avg_risk,
        "region_data": region_data,
        "pie_data": pie_data,
        "shipping_mode_data": shipping_mode_data,
        "is_staff": request.user.is_staff
    })

@csrf_exempt
def get_shipments(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)
    
    qs = Shipment.objects.all().order_by('-created_at') if request.user.is_staff else Shipment.objects.filter(user=request.user).order_by('-created_at')
    
    data = [{
        "id": s.id,
        "shipping_mode": s.shipping_mode,
        "order_region": s.order_region,
        "predicted_risk": s.predicted_risk,
        "predicted_class": s.predicted_class,
        "actual_status": s.actual_status,
        "created_at": s.created_at.strftime("%Y-%m-%d %H:%M")
    } for s in qs[:50]]
    
    return JsonResponse({"status": "success", "data": data})

@csrf_exempt
def update_shipment_status(request, shipment_id):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            shipment = Shipment.objects.get(id=shipment_id)
            if not request.user.is_staff and shipment.user != request.user:
                return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)
            
            shipment.actual_status = data.get("actual_status", "PENDING")
            shipment.save()
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

@csrf_exempt
def get_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)
    
    if not request.user.is_staff:
        return JsonResponse({"status": "success", "data": []})
        
    qs = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
    data = [{
        "id": n.id,
        "message_en": n.message_en,
        "message_ar": n.message_ar,
        "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
    } for n in qs]
    
    return JsonResponse({"status": "success", "data": data})

@csrf_exempt
def batch_predict(request):
    if not request.user.is_authenticated:
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=401)
    
    if request.method == 'POST':
        try:
            data_list = json.loads(request.body)
            results = []
            for data in data_list:
                risk = min(0.99, max(0.01, random.uniform(0.1, 0.9))) # Mock prediction for batch
                p_class = "LATE" if risk > 0.5 else "ON-TIME"
                
                Shipment.objects.create(
                    user=request.user,
                    shipping_mode=data.get('shipping_mode', 'Standard Class'),
                    order_region=data.get('order_region', 'Western Europe'),
                    market=data.get('market', 'Europe'),
                    transaction_type=data.get('type', 'DEBIT'),
                    customer_segment=data.get('customer_segment', 'Consumer'),
                    predicted_risk=risk,
                    predicted_class=p_class
                )
                
                results.append({
                    "region": data.get('order_region', 'Unknown'),
                    "predicted_risk": risk,
                    "predicted_class": p_class
                })
                
            return JsonResponse({"status": "success", "results": results})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)

@csrf_exempt
def submit_delay_report(request):
    if request.method == "POST":
        try:
            from .models import DelayReport
            tracking_number = request.POST.get('tracking_number')
            reporter_name = request.POST.get('reporter_name')
            reporter_email = request.POST.get('reporter_email')
            message = request.POST.get('message')
            image = request.FILES.get('image')

            if not tracking_number or not message:
                return JsonResponse({"status": "error", "message": "Missing fields"}, status=400)

            report = DelayReport.objects.create(
                tracking_number=tracking_number,
                reporter_name=reporter_name,
                reporter_email=reporter_email,
                message=message,
                image=image
            )
            return JsonResponse({"status": "success", "report_id": report.id})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)
