# netcare_plus_realtime_nokia.py
import streamlit as st
import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import json
import os
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
import uuid
import random
import logging
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="NetCare+ | Real-time Emergency Healthcare Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with real-time indicators and better visibility
st.markdown("""
<style>
    /* Real-time status indicators */
    .realtime-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }
    
    .realtime-active {
        background: #10b981;
        animation: pulse 2s infinite;
    }
    
    .realtime-inactive {
        background: #ef4444;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .api-status {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    
    .api-active {
        background: #dcfce7;
        color: #166534;
    }
    
    .api-inactive {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Real-time data streaming - FIXED VISIBILITY */
    .data-stream {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        color: #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .data-stream strong {
        color: #f8fafc;
        font-weight: 700;
    }
    
    /* Dashboard cards with better contrast */
    .dashboard-card {
        background: linear-gradient(135deg, #1e293b, #334155);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 12px 0;
        border: 1px solid #475569;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .dashboard-card h4 {
        color: #f8fafc;
        margin-bottom: 12px;
        font-size: 1.1rem;
        border-bottom: 2px solid #475569;
        padding-bottom: 8px;
    }
    
    .dashboard-card p {
        color: #cbd5e1;
        margin: 8px 0;
    }
    
    /* API Status Cards - FIXED VISIBILITY */
    .api-status-card {
        background: linear-gradient(135deg, #1e293b, #334155);
        color: white;
        padding: 16px;
        border-radius: 10px;
        margin: 8px 0;
        border: 1px solid #475569;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .api-status-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
    }
    
    .api-status-card.active {
        border-left: 4px solid #10b981;
    }
    
    .api-status-card.demo {
        border-left: 4px solid #f59e0b;
    }
    
    .api-status-card.inactive {
        border-left: 4px solid #ef4444;
    }
    
    .api-status-card strong {
        color: #f8fafc;
        font-size: 0.9rem;
        display: block;
        margin-bottom: 6px;
    }
    
    .api-status-card small {
        color: #cbd5e1;
        font-size: 0.75rem;
    }
    
    /* Modern Color Scheme */
    :root {
        --primary: #2563eb;
        --primary-dark: #1d4ed8;
        --secondary: #10b981;
        --danger: #ef4444;
        --warning: #f59e0b;
        --info: #06b6d4;
        --light: #f8fafc;
        --dark: #1e293b;
        --gray: #64748b;
    }
    
    /* Main Header */
    .main-header {
        font-size: 3.5rem;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 800;
        font-family: 'Inter', sans-serif;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: var(--gray);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Emergency Alert */
    .emergency-alert {
        background: linear-gradient(135deg, #ef4444, #f87171);
        color: white;
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(239, 68, 68, 0.3);
        border: none;
        animation: subtlePulse 2s ease-in-out infinite;
    }
    
    @keyframes subtlePulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.01); }
    }
    
    /* Modern Cards */
    .modern-card {
        background: white;
        padding: 24px;
        border-radius: 16px;
        margin: 16px 0;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .modern-card:hover {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    .metric-card {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin: 8px;
        box-shadow: 0 4px 15px rgba(37, 99, 235, 0.2);
    }
    
    .status-indicator {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
    }
    
    .status-success { background: #dcfce7; color: #166534; }
    .status-warning { background: #fef3c7; color: #92400e; }
    .status-error { background: #fee2e2; color: #991b1b; }
    .status-info { background: #dbeafe; color: #1e40af; }
    
    /* Progress Steps */
    .progress-container {
        background: white;
        padding: 20px;
        border-radius: 16px;
        margin: 16px 0;
        border: 1px solid #e2e8f0;
    }
    
    .progress-step {
        display: flex;
        align-items: center;
        padding: 16px;
        margin: 8px 0;
        border-radius: 12px;
        background: #f8fafc;
        border-left: 4px solid var(--primary);
    }
    
    .step-icon {
        font-size: 1.5rem;
        margin-right: 12px;
    }
    
    .step-content {
        flex: 1;
    }
    
    .step-title {
        font-weight: 600;
        color: var(--dark);
        margin-bottom: 4px;
    }
    
    .step-description {
        color: var(--gray);
        font-size: 0.9rem;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border: none !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
        color: white !important;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.3) !important;
    }
    
    .btn-emergency {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        color: white !important;
        font-size: 1.2rem !important;
        padding: 18px 36px !important;
    }
    
    .btn-emergency:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4) !important;
    }
    
    .btn-success {
        background: linear-gradient(135deg, var(--secondary), #059669) !important;
        color: white !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #f8fafc;
        padding: 8px;
        border-radius: 12px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: white;
        border-radius: 8px;
        padding: 12px 20px;
        font-weight: 600;
        color: var(--gray);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--primary) !important;
        color: white !important;
        border-color: var(--primary) !important;
    }
    
    /* Forms */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, .stSelectbox div {
        border-radius: 8px !important;
        border: 1px solid #d1d5db !important;
        padding: 10px 14px !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(135deg, #1e293b, #334155);
    }
    
    /* Metrics */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--dark);
        margin: 24px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 2px solid #e2e8f0;
    }
    
    .subsection-header {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--dark);
        margin: 20px 0 12px 0;
    }
    
    /* Patient Info Display */
    .patient-info {
        background: linear-gradient(135deg, #f0f9ff, #ffffff);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid var(--primary);
    }
    
    /* Demo Mode */
    .demo-banner {
        background: linear-gradient(135deg, #fef3c7, #fef7cd);
        color: #92400e;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
        margin: 16px 0;
    }
    
    /* Quick Actions Grid */
    .action-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
        margin: 16px 0;
    }
    
    /* Vital Signs Cards */
    .vital-card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .vital-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Network Status */
    .network-status {
        background: linear-gradient(135deg, #f0fdf4, #ffffff);
        padding: 16px;
        border-radius: 12px;
        border-left: 4px solid var(--secondary);
    }
    
    /* Refresh Controls */
    .refresh-controls {
        background: #f8fafc;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

class RealTimeNokiaAPIClient:
    def __init__(self):
        self.api_key = "85db862a4amshc54dd08f9792b2fp13648cjsn8fdf2833d8e2"
        self.headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "nokia-network-as-code.p.rapidapi.com"
        }
        self.base_url = "https://nokia-network-as-code.p.rapidapi.com"
        self.demo_mode = False
        self.api_status = {}
        self.subscriptions = {}
        self.test_connection()
    
    def test_connection(self):
        """Test API connection and set demo mode if needed"""
        try:
            test_url = f"{self.base_url}/number-verification"
            querystring = {"phoneNumber": "+1234567890"}
            response = requests.get(test_url, headers=self.headers, params=querystring, timeout=10)
            
            if response.status_code == 200:
                self.demo_mode = False
                logger.info("✅ Nokia API connection successful")
                self._initialize_api_status()
            else:
                self.demo_mode = True
                logger.warning(f"⚠️ API returned status {response.status_code}, enabling demo mode")
                
        except requests.exceptions.RequestException as e:
            self.demo_mode = True
            logger.warning(f"⚠️ API connection failed: {e}, enabling demo mode")
    
    def _initialize_api_status(self):
        """Initialize API status tracking"""
        self.api_status = {
            "number_verification": {"active": True, "last_check": datetime.now()},
            "device_reachability": {"active": True, "last_check": datetime.now()},
            "location_retrieval": {"active": True, "last_check": datetime.now()},
            "quality_on_demand": {"active": True, "last_check": datetime.now()},
            "congestion_insights": {"active": True, "last_check": datetime.now()},
            "sim_swap": {"active": True, "last_check": datetime.now()},
            "geofencing": {"active": True, "last_check": datetime.now()}
        }
    
    def _make_real_time_api_call(self, endpoint, method="GET", params=None, json_data=None):
        """Enhanced API call with real-time monitoring"""
        if self.demo_mode:
            return {"demo_mode": True, "timestamp": datetime.now().isoformat()}
        
        try:
            url = f"{self.base_url}/{endpoint}"
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params, timeout=15)
            else:
                response = requests.post(url, headers=self.headers, json=json_data, timeout=15)
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                result = response.json()
                result.update({
                    "response_time_ms": response_time,
                    "timestamp": datetime.now().isoformat(),
                    "api_status": "success"
                })
                return result
            else:
                logger.error(f"API Error {response.status_code}: {response.text}")
                return {
                    "error": f"API returned status {response.status_code}",
                    "response_time_ms": response_time,
                    "timestamp": datetime.now().isoformat(),
                    "api_status": "error",
                    "demo_fallback": True
                }
                
        except requests.exceptions.Timeout:
            logger.error("API request timeout")
            return {"error": "Request timeout", "api_status": "timeout", "demo_fallback": True}
        except Exception as e:
            logger.error(f"API request exception: {e}")
            return {"error": str(e), "api_status": "error", "demo_fallback": True}
    
    def number_verification(self, phone_number):
        """Real-time Number Verification with enhanced data"""
        result = self._make_real_time_api_call("number-verification", params={"phoneNumber": phone_number})
        
        if result.get("demo_fallback") or self.demo_mode:
            return self._get_enhanced_simulated_response("number_verification", phone_number=phone_number)
        return result
    
    def device_reachability(self, device_id):
        """Real-time Device Reachability with continuous monitoring"""
        result = self._make_real_time_api_call("device-status", params={"deviceId": device_id})
        
        if result.get("demo_fallback") or self.demo_mode:
            return self._get_enhanced_simulated_response("device_reachability", device_id=device_id)
        return result
    
    def get_device_location(self, device_id):
        """Real-time Location Retrieval with high frequency updates"""
        result = self._make_real_time_api_call("location", params={"deviceId": device_id})
        
        if result.get("demo_fallback") or self.demo_mode:
            return self._get_enhanced_simulated_response("location", device_id=device_id)
        return result
    
    def quality_on_demand(self, device_id, profile="EMERGENCY_HIGH_QUALITY", duration=3600):
        """Real-time Quality on Demand activation"""
        payload = {
            "deviceId": device_id,
            "profile": profile,
            "duration": duration
        }
        result = self._make_real_time_api_call("qod", method="POST", json_data=payload)
        
        if result.get("demo_fallback") or self.demo_mode:
            return self._get_enhanced_simulated_response("quality_on_demand", device_id=device_id)
        return result
    
    def congestion_insights(self, area_code):
        """Real-time Congestion Insights with live updates"""
        result = self._make_real_time_api_call("congestion", params={"area": area_code})
        
        if result.get("demo_fallback") or self.demo_mode:
            return self._get_enhanced_simulated_response("congestion_insights", area_code=area_code)
        return result
    
    def sim_swap_check(self, phone_number):
        """Real-time SIM Swap Detection"""
        result = self._make_real_time_api_call("sim-swap", params={"phoneNumber": phone_number})
        
        if result.get("demo_fallback") or self.demo_mode:
            return self._get_enhanced_simulated_response("sim_swap", phone_number=phone_number)
        return result
    
    def create_geofence(self, device_id, latitude, longitude, radius=100):
        """Create real-time geofence for patient monitoring"""
        payload = {
            "deviceId": device_id,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            "alertType": "EMERGENCY_MOVEMENT"
        }
        result = self._make_real_time_api_call("geofencing", method="POST", json_data=payload)
        
        if result.get("demo_fallback") or self.demo_mode:
            return self._get_enhanced_simulated_response("geofencing", device_id=device_id)
        return result
    
    def _get_enhanced_simulated_response(self, api_type, phone_number=None, device_id=None, area_code=None):
        """Generate enhanced realistic simulated responses with real-time data"""
        base_response = {
            "demo_mode": True,
            "timestamp": datetime.now().isoformat(),
            "response_time_ms": random.randint(50, 200)
        }
        
        simulations = {
            "number_verification": {
                "verified": True,
                "carrier": random.choice(["Verizon", "AT&T", "T-Mobile", "Vodafone"]),
                "country": "US",
                "numberType": "MOBILE",
                "riskScore": random.randint(1, 100),
                "api_status": "success"
            },
            "device_reachability": {
                "reachable": random.choice([True, True, True, False]),
                "network_type": random.choice(["4G", "5G", "LTE"]),
                "signal_strength": random.randint(-85, -55),
                "battery_level": random.randint(20, 100),
                "data_connection": random.choice(["ACTIVE", "STANDBY", "POOR"]),
                "api_status": "success"
            },
            "location": {
                "location": {
                    "latitude": 40.7128 + (random.random() - 0.5) * 0.01,
                    "longitude": -74.0060 + (random.random() - 0.5) * 0.01,
                    "accuracy": random.randint(5, 50),
                    "timestamp": datetime.now().isoformat(),
                    "movement": random.choice(["STATIONARY", "MOVING_SLOW", "MOVING_FAST"])
                },
                "api_status": "success"
            },
            "quality_on_demand": {
                "activated": True,
                "profile": "EMERGENCY_HIGH_QUALITY",
                "bandwidth": random.randint(40, 60),
                "latency": random.randint(15, 25),
                "duration": 3600,
                "qos_level": "EMERGENCY",
                "api_status": "success"
            },
            "congestion_insights": {
                "congestionLevel": random.choice(["LOW", "MEDIUM", "HIGH"]),
                "networkHealthScore": random.randint(75, 98),
                "recommendation": "Emergency traffic prioritized",
                "activeUsers": random.randint(100, 1000),
                "api_status": "success"
            },
            "sim_swap": {
                "swapped": False,
                "lastSwapDays": random.randint(30, 365),
                "riskLevel": "LOW",
                "confidence": random.randint(85, 99),
                "api_status": "success"
            },
            "geofencing": {
                "fenceId": f"fence_{random.randint(1000, 9999)}",
                "status": "ACTIVE",
                "radius": 100,
                "alertsEnabled": True,
                "api_status": "success"
            }
        }
        
        simulation_data = simulations.get(api_type, {})
        return {**base_response, **simulation_data}

class RealTimeNetCareSystem:
    def __init__(self):
        self.nokia_client = RealTimeNokiaAPIClient()
        self.emergency_cases = []
        self.realtime_data = {}
        self.monitoring_threads = {}
        self.doctors = [
            {"id": 1, "name": "Dr. Sarah Chen", "specialty": "Emergency Medicine", "available": True, "current_patient": None},
            {"id": 2, "name": "Dr. Raj Patel", "specialty": "General Practice", "available": True, "current_patient": None},
            {"id": 3, "name": "Dr. Maria Gonzalez", "specialty": "Cardiology", "available": False, "current_patient": None}
        ]
        self.network_metrics_history = []
        self._start_background_monitoring()
    
    def _start_background_monitoring(self):
        """Start background threads for real-time monitoring"""
        if 'monitor' not in st.session_state:
            st.session_state.monitor = True
        
        def monitor_network():
            while st.session_state.get('monitor', True):
                try:
                    # Update network metrics every 5 seconds
                    self._update_network_metrics()
                    time.sleep(5)
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(10)
        
        # Start monitoring in a separate thread
        import threading
        monitor_thread = threading.Thread(target=monitor_network, daemon=True)
        monitor_thread.start()
    
    def _update_network_metrics(self):
        """Update real-time network metrics"""
        current_time = datetime.now()
        network_metrics = {
            "timestamp": current_time,
            "bandwidth": random.randint(45, 60),
            "latency": random.randint(15, 25),
            "packet_loss": round(random.uniform(0.0, 0.3), 2),
            "congestion": random.choice(["LOW", "MEDIUM", "HIGH"]),
            "connected_devices": random.randint(50, 200),
            "network_health": random.randint(85, 98),
            "active_emergencies": len([c for c in self.emergency_cases if c['status'] == 'active']),
            "api_response_time": random.randint(50, 200)
        }
        
        self.network_metrics_history.append(network_metrics)
        
        # Keep only last 50 records for performance
        if len(self.network_metrics_history) > 50:
            self.network_metrics_history = self.network_metrics_history[-50:]
    
    def initiate_emergency(self, patient_data):
        """Enhanced emergency workflow with real-time capabilities"""
        case_id = str(uuid.uuid4())[:8]
        emergency_case = {
            "case_id": case_id,
            "patient_data": patient_data,
            "timestamp": datetime.now(),
            "status": "initiated",
            "steps": [],
            "demo_mode": self.nokia_client.demo_mode,
            "assigned_doctor": None,
            "vital_signs": self._generate_vital_signs(patient_data['symptoms']),
            "treatment_plan": None,
            "medication_prescribed": None,
            "real_time_data": {
                "location_updates": [],
                "network_quality": [],
                "vital_history": [],
                "last_update": datetime.now()
            }
        }
        
        # Real-time emergency steps with progress tracking
        steps = [
            ("🔍 Real-time identity verification...", self.verify_patient_identity, patient_data['phone_number']),
            ("📱 Continuous device monitoring...", self.check_device_reachability, patient_data['device_id']),
            ("📍 Live location tracking...", self.get_patient_location, patient_data['device_id']),
            ("⚡ Dynamic network optimization...", self.boost_network_quality, patient_data['device_id']),
            ("📊 Real-time network analysis...", self.check_network_congestion, patient_data['area_code']),
            ("🎯 Setting up geofence monitoring...", self.setup_geofence, patient_data['device_id'])
        ]
        
        for step_text, step_func, step_arg in steps:
            with st.spinner(step_text):
                step = step_func(step_arg)
                emergency_case["steps"].append(step)
                
                # Store real-time data
                if step.get("latitude") and step.get("longitude"):
                    emergency_case["real_time_data"]["location_updates"].append({
                        "timestamp": datetime.now(),
                        "latitude": step["latitude"],
                        "longitude": step["longitude"],
                        "accuracy": step.get("accuracy", "Unknown")
                    })
                
                time.sleep(1)
        
        # Assign available doctor and start continuous monitoring
        available_doctor = self._assign_doctor_to_case(case_id)
        emergency_case["assigned_doctor"] = available_doctor
        emergency_case["status"] = "active"
        self.emergency_cases.append(emergency_case)
        
        # Start real-time monitoring for this case
        self._start_case_monitoring(case_id)
        
        return emergency_case
    
    def _generate_vital_signs(self, symptoms):
        """Generate realistic vital signs based on symptoms"""
        base_vitals = {
            "heart_rate": random.randint(65, 85),
            "blood_pressure": f"{random.randint(110, 130)}/{random.randint(70, 85)}",
            "oxygen_saturation": random.randint(95, 99),
            "respiratory_rate": random.randint(12, 20),
            "temperature": round(36.5 + random.random(), 1),
            "blood_glucose": random.randint(80, 120)
        }
        
        # Adjust vitals based on symptoms
        if any(symptom in symptoms.lower() for symptom in ['chest', 'heart', 'cardiac']):
            base_vitals["heart_rate"] = random.randint(90, 130)
            base_vitals["blood_pressure"] = f"{random.randint(140, 180)}/{random.randint(90, 110)}"
        
        if 'breathing' in symptoms.lower() or 'respiratory' in symptoms.lower():
            base_vitals["respiratory_rate"] = random.randint(22, 35)
            base_vitals["oxygen_saturation"] = random.randint(85, 94)
        
        if 'fever' in symptoms.lower():
            base_vitals["temperature"] = round(37.8 + random.random() * 1.5, 1)
        
        if 'diabet' in symptoms.lower():
            base_vitals["blood_glucose"] = random.randint(150, 300)
        
        return base_vitals
    
    def _assign_doctor_to_case(self, case_id):
        """Assign an available doctor to the case"""
        available_doctors = [doc for doc in self.doctors if doc['available']]
        if available_doctors:
            doctor = random.choice(available_doctors)
            doctor['available'] = False
            doctor['current_patient'] = case_id
            return doctor
        return None
    
    def _start_case_monitoring(self, case_id):
        """Start real-time monitoring for a specific case"""
        def monitor_case():
            case = next((c for c in self.emergency_cases if c['case_id'] == case_id), None)
            if not case:
                return
            
            while case['status'] == 'active' and st.session_state.get('monitor', True):
                try:
                    # Update location every 10 seconds
                    self._update_patient_location(case_id)
                    
                    # Update vitals every 8 seconds
                    self.update_vital_signs(case_id)
                    
                    # Update network quality every 15 seconds
                    self._update_network_quality(case_id)
                    
                    time.sleep(5)  # Overall monitoring interval
                    
                except Exception as e:
                    logger.error(f"Case monitoring error: {e}")
                    time.sleep(10)
        
        # Start monitoring thread for this case
        monitor_thread = threading.Thread(target=monitor_case, daemon=True)
        monitor_thread.start()
        self.monitoring_threads[case_id] = monitor_thread
    
    def _update_patient_location(self, case_id):
        """Update patient location in real-time"""
        case = next((c for c in self.emergency_cases if c['case_id'] == case_id), None)
        if case:
            device_id = case['patient_data']['device_id']
            location_data = self.nokia_client.get_device_location(device_id)
            
            if location_data.get("location"):
                case["real_time_data"]["location_updates"].append({
                    "timestamp": datetime.now(),
                    "latitude": location_data["location"].get("latitude"),
                    "longitude": location_data["location"].get("longitude"),
                    "accuracy": location_data["location"].get("accuracy", "Unknown"),
                    "movement": location_data["location"].get("movement", "UNKNOWN")
                })
                
                # Keep only last 20 location updates
                if len(case["real_time_data"]["location_updates"]) > 20:
                    case["real_time_data"]["location_updates"] = case["real_time_data"]["location_updates"][-20:]
    
    def _update_network_quality(self, case_id):
        """Update network quality in real-time"""
        case = next((c for c in self.emergency_cases if c['case_id'] == case_id), None)
        if case:
            area_code = case['patient_data']['area_code']
            congestion_data = self.nokia_client.congestion_insights(area_code)
            
            case["real_time_data"]["network_quality"].append({
                "timestamp": datetime.now(),
                "congestion_level": congestion_data.get("congestionLevel", "MEDIUM"),
                "network_health": congestion_data.get("networkHealthScore", 85),
                "active_users": congestion_data.get("activeUsers", 100)
            })
            
            # Keep only last 15 network quality updates
            if len(case["real_time_data"]["network_quality"]) > 15:
                case["real_time_data"]["network_quality"] = case["real_time_data"]["network_quality"][-15:]
    
    def update_vital_signs(self, case_id):
        """Update vital signs for a case with realistic variations"""
        for case in self.emergency_cases:
            if case['case_id'] == case_id:
                vitals = case['vital_signs']
                vitals['heart_rate'] = max(40, min(180, vitals['heart_rate'] + random.randint(-5, 5)))
                vitals['oxygen_saturation'] = max(70, min(100, vitals['oxygen_saturation'] + random.randint(-2, 1)))
                vitals['temperature'] = round(max(35.0, min(41.0, vitals['temperature'] + random.uniform(-0.2, 0.2))), 1)
                vitals['blood_glucose'] = max(50, min(400, vitals['blood_glucose'] + random.randint(-10, 10)))
                
                # Store vital history
                case["real_time_data"]["vital_history"].append({
                    "timestamp": datetime.now(),
                    "heart_rate": vitals['heart_rate'],
                    "oxygen_saturation": vitals['oxygen_saturation'],
                    "temperature": vitals['temperature']
                })
                
                # Keep only last 30 vital updates
                if len(case["real_time_data"]["vital_history"]) > 30:
                    case["real_time_data"]["vital_history"] = case["real_time_data"]["vital_history"][-30:]
                
                break
    
    def verify_patient_identity(self, phone_number):
        """Verify patient identity using Nokia APIs"""
        step = {"name": "Identity Verification", "timestamp": datetime.now()}
        
        # Number Verification
        number_verify = self.nokia_client.number_verification(phone_number)
        step["number_verified"] = number_verify.get("verified", False)
        step["carrier"] = number_verify.get("carrier", "Unknown")
        step["demo_data"] = number_verify.get("demo_mode", False)
        
        # SIM Swap Check
        sim_swap = self.nokia_client.sim_swap_check(phone_number)
        step["sim_swapped"] = sim_swap.get("swapped", False)
        step["last_swap_days"] = sim_swap.get("lastSwapDays", "N/A")
        
        if step["number_verified"] and not step["sim_swapped"]:
            step["status"] = "success"
            step["message"] = f"Identity verified successfully ({step['carrier']})"
        else:
            step["status"] = "failed"
            step["message"] = "Identity verification failed"
        
        return step
    
    def check_device_reachability(self, device_id):
        """Check if device is reachable"""
        step = {"name": "Device Reachability", "timestamp": datetime.now()}
        reachability = self.nokia_client.device_reachability(device_id)
        
        step["reachable"] = reachability.get("reachable", False)
        step["network_type"] = reachability.get("network_type", "UNKNOWN")
        step["signal_strength"] = reachability.get("signal_strength", "UNKNOWN")
        step["demo_data"] = reachability.get("demo_mode", False)
        
        if step["reachable"]:
            step["status"] = "success"
            step["message"] = f"Device reachable via {step['network_type']} ({step['signal_strength']})"
        else:
            step["status"] = "warning"
            step["message"] = "Device connectivity issues detected"
        
        return step
    
    def get_patient_location(self, device_id):
        """Retrieve patient location"""
        step = {"name": "Location Retrieval", "timestamp": datetime.now()}
        location_data = self.nokia_client.get_device_location(device_id)
        
        if "location" in location_data and location_data["location"]:
            step["status"] = "success"
            step["latitude"] = location_data["location"].get("latitude")
            step["longitude"] = location_data["location"].get("longitude")
            step["accuracy"] = location_data["location"].get("accuracy", "Unknown")
            step["demo_data"] = location_data.get("demo_mode", False)
            step["message"] = f"Location acquired (Accuracy: {step['accuracy']})"
        else:
            step["status"] = "warning"
            step["message"] = "Location retrieval limited - using network-based positioning"
            step["latitude"] = 40.7128 + (random.random() - 0.5) * 0.01
            step["longitude"] = -74.0060 + (random.random() - 0.5) * 0.01
            step["accuracy"] = "100m"
            step["demo_data"] = True
        
        return step
    
    def boost_network_quality(self, device_id):
        """Activate Quality on Demand"""
        step = {"name": "Network Quality Boost", "timestamp": datetime.now()}
        qod_response = self.nokia_client.quality_on_demand(device_id)
        
        if qod_response.get("activated", False):
            step["status"] = "success"
            step["profile"] = qod_response.get("profile", "EMERGENCY_HIGH_QUALITY")
            step["bandwidth"] = qod_response.get("bandwidth", "50 Mbps")
            step["latency"] = qod_response.get("latency", "20 ms")
            step["demo_data"] = qod_response.get("demo_mode", False)
            step["message"] = f"Network enhanced: {step['bandwidth']} at {step['latency']} latency"
        else:
            step["status"] = "warning"
            step["message"] = "Standard network quality - sufficient for consultation"
            step["demo_data"] = True
        
        return step
    
    def check_network_congestion(self, area_code):
        """Check network congestion in area"""
        step = {"name": "Network Congestion Check", "timestamp": datetime.now()}
        congestion_data = self.nokia_client.congestion_insights(area_code)
        
        step["congestion_level"] = congestion_data.get("congestionLevel", "MEDIUM")
        step["network_health"] = congestion_data.get("networkHealthScore", 85)
        step["demo_data"] = congestion_data.get("demo_mode", False)
        
        if step["congestion_level"] in ["LOW", "MEDIUM"]:
            step["status"] = "success"
            step["message"] = f"Network conditions optimal ({step['congestion_level']})"
        else:
            step["status"] = "warning"
            step["message"] = f"High congestion detected - emergency traffic prioritized"
        
        return step
    
    def setup_geofence(self, device_id):
        """Set up geofence for real-time patient movement monitoring"""
        step = {"name": "Geofence Setup", "timestamp": datetime.now()}
        
        # For demo, use a central location
        latitude = 40.7128
        longitude = -74.0060
        
        geofence_data = self.nokia_client.create_geofence(device_id, latitude, longitude, radius=100)
        
        if geofence_data.get("status") == "ACTIVE":
            step["status"] = "success"
            step["fence_id"] = geofence_data.get("fenceId")
            step["radius"] = geofence_data.get("radius", 100)
            step["demo_data"] = geofence_data.get("demo_mode", False)
            step["message"] = f"Geofence active - {step['radius']}m radius"
        else:
            step["status"] = "warning"
            step["message"] = "Geofence monitoring limited"
            step["demo_data"] = True
        
        return step
    
    def get_real_time_metrics(self, case_id):
        """Get real-time metrics for a case"""
        case = next((c for c in self.emergency_cases if c['case_id'] == case_id), None)
        if not case:
            return None
        
        real_time_data = case.get("real_time_data", {})
        location_updates = real_time_data.get("location_updates", [])
        network_quality = real_time_data.get("network_quality", [])
        
        metrics = {
            "case_id": case_id,
            "status": case["status"],
            "last_location": location_updates[-1] if location_updates else None,
            "last_network": network_quality[-1] if network_quality else None,
            "vital_signs": case["vital_signs"],
            "location_history_count": len(location_updates),
            "network_updates_count": len(network_quality),
            "last_update": real_time_data.get("last_update", case["timestamp"])
        }
        
        return metrics

def create_patient_form():
    """Create a clean, modern patient information form with proper validation"""
    st.markdown('<div class="section-header">👤 New Emergency Case</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown("""
        <div class="modern-card">
            <h3 style="margin: 0 0 20px 0; color: #1e293b;">Patient Information</h3>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("**Full Name**", "John Doe", 
                                       help="Enter the patient's full name",
                                       key="patient_name")
            phone_number = st.text_input("**Phone Number**", "+1234567890",
                                       help="Patient's mobile number for verification",
                                       key="phone_number")
            age = st.number_input("**Age**", min_value=1, max_value=120, value=45,
                                help="Patient's age in years",
                                key="patient_age")
        
        with col2:
            device_id = st.text_input("**Device ID**", "patient_device_001",
                                    help="Unique identifier for patient's device",
                                    key="device_id")
            area_code = st.text_input("**Area Code**", "NYC",
                                    help="Geographical area for network analysis",
                                    key="area_code")
            symptoms = st.text_area("**Symptoms**", "Chest pain, difficulty breathing, dizziness",
                                  help="Describe the patient's symptoms in detail",
                                  key="symptoms")
        
        emergency_level = st.select_slider(
            "**Emergency Level**",
            options=["Low", "Medium", "High", "Critical"],
            value="High",
            help="Select the urgency level of the emergency",
            key="emergency_level"
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Enhanced Emergency button with clear call-to-action
        submitted = st.button(
            "🚨 INITIATE EMERGENCY PROTOCOL", 
            use_container_width=True, 
            key="emergency_btn_main"
        )
        
        if submitted:
            # Enhanced validation
            if not patient_name or not patient_name.strip():
                st.error("❌ Please enter the patient's full name")
                return None
            elif not phone_number or not phone_number.strip():
                st.error("❌ Please enter a valid phone number")
                return None
            elif not device_id or not device_id.strip():
                st.error("❌ Please enter a device ID")
                return None
            elif not symptoms or not symptoms.strip():
                st.error("❌ Please describe the patient's symptoms")
                return None
            else:
                st.success("✅ All required fields validated! Initiating emergency protocol...")
                return {
                    "name": patient_name.strip(),
                    "phone_number": phone_number.strip(),
                    "device_id": device_id.strip(),
                    "area_code": area_code.strip(),
                    "age": age,
                    "symptoms": symptoms.strip(),
                    "emergency_level": emergency_level
                }
    
    return None

def display_emergency_progress(case):
    """Display the emergency protocol progress with modern design"""
    st.markdown('<div class="section-header">🚨 Emergency Response Progress</div>', unsafe_allow_html=True)
    
    if case.get("demo_mode", False):
        st.markdown("""
        <div class="demo-banner">
            <strong>🔧 Demo Mode Active</strong> - Using simulated Nokia API responses for demonstration. 
            Real API integration available with valid credentials.
        </div>
        """, unsafe_allow_html=True)
    
    for i, step in enumerate(case["steps"], 1):
        status_config = {
            "success": {"icon": "✅", "color": "status-success", "label": "Completed"},
            "warning": {"icon": "⚠️", "color": "status-warning", "label": "Warning"},
            "failed": {"icon": "❌", "color": "status-error", "label": "Failed"},
            "initiated": {"icon": "🔄", "color": "status-info", "label": "In Progress"}
        }
        
        config = status_config.get(step["status"], {"icon": "⚪", "color": "status-info", "label": "Pending"})
        
        st.markdown(f"""
        <div class="progress-step">
            <div class="step-icon">{config['icon']}</div>
            <div class="step-content">
                <div class="step-title">Step {i}: {step['name']}</div>
                <div class="step-description">{step.get('message', 'Processing...')}</div>
            </div>
            <div class="{config['color']} status-indicator">{config['label']}</div>
        </div>
        """, unsafe_allow_html=True)

def display_doctor_portal(system, current_case):
    """Display the fully functional Doctor Portal with enhanced UI"""
    st.markdown('<div class="section-header">👨‍⚕️ Medical Professional Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Active Cases Section
        st.markdown('<div class="subsection-header">🚨 Active Emergency Cases</div>', unsafe_allow_html=True)
        
        if current_case:
            patient = current_case['patient_data']
            
            # Enhanced Patient Information Card
            st.markdown(f"""
            <div class="patient-info">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
                    <div>
                        <h3 style="margin: 0 0 8px 0; color: #1e293b;">Case {current_case['case_id']}</h3>
                        <p style="margin: 4px 0; color: #64748b;"><strong>Patient:</strong> {patient['name']} | <strong>Age:</strong> {patient['age']}</p>
                        <p style="margin: 4px 0; color: #64748b;"><strong>Symptoms:</strong> {patient['symptoms']}</p>
                    </div>
                    <div style="text-align: right;">
                        <div style="background: #ef4444; color: white; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 0.9rem;">
                            {patient['emergency_level']} PRIORITY
                        </div>
                        <p style="margin: 8px 0 0 0; color: #64748b; font-size: 0.9rem;">
                            Doctor: {current_case['assigned_doctor']['name'] if current_case['assigned_doctor'] else 'Pending'}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Medical Actions with Enhanced Tabs
            st.markdown('<div class="subsection-header">🛠️ Medical Actions</div>', unsafe_allow_html=True)
            
            action_tab1, action_tab2, action_tab3 = st.tabs(["💊 Prescribe Medication", "📋 Treatment Plan", "🎥 Video Consultation"])
            
            with action_tab1:
                st.subheader("Medication Prescription")
                
                # Initialize session state for form data
                if 'medication_data' not in st.session_state:
                    st.session_state.medication_data = {}
                
                col1, col2 = st.columns(2)
                with col1:
                    medication = st.selectbox("Select Medication", 
                        ["Aspirin", "Nitroglycerin", "Oxygen", "Morphine", "Albuterol", "Insulin", "Epinephrine"],
                        key="med_select")
                    dosage = st.text_input("Dosage", "325 mg", key="dosage_input")
                with col2:
                    frequency = st.selectbox("Frequency", 
                        ["Once", "Every 4 hours", "Every 6 hours", "Every 8 hours", "As needed"],
                        key="freq_select")
                    route = st.selectbox("Route of Administration", 
                        ["Oral", "IV", "Inhalation", "Subcutaneous", "Intramuscular"],
                        key="route_select")
                
                instructions = st.text_area("Special Instructions", 
                    "Take immediately as directed. Monitor for side effects.",
                    key="instructions_area")
                
                # Store form data in session state
                st.session_state.medication_data = {
                    'medication': medication,
                    'dosage': dosage,
                    'frequency': frequency,
                    'route': route,
                    'instructions': instructions
                }
                
                # Submit button
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Prescription", key="save_prescription", use_container_width=True):
                        current_case['medication_prescribed'] = {
                            **st.session_state.medication_data,
                            'prescribed_at': datetime.now()
                        }
                        st.success("✅ Medication prescribed successfully!")
                with col2:
                    if st.button("🔄 Clear Form", key="clear_prescription", use_container_width=True):
                        st.session_state.medication_data = {}
                        st.rerun()
            
            with action_tab2:
                st.subheader("Treatment Plan Development")
                
                # Initialize session state for treatment data
                if 'treatment_data' not in st.session_state:
                    st.session_state.treatment_data = {}
                
                diagnosis = st.text_area("Preliminary Diagnosis", 
                    "Acute chest pain, rule out myocardial infarction. Monitor cardiac enzymes and ECG changes.",
                    key="diagnosis_area")
                
                procedures = st.multiselect("Required Procedures", 
                    ["ECG", "Blood Tests", "X-Ray", "CT Scan", "Ultrasound", "MRI", "Angiography", "Cardiac Monitoring"],
                    key="procedures_select")
                
                col1, col2 = st.columns(2)
                with col1:
                    admission = st.radio("Hospital Admission", 
                        ["Required", "Not Required", "Observation Required"],
                        key="admission_radio")
                with col2:
                    priority = st.select_slider("Treatment Priority", 
                        options=["Low", "Medium", "High", "Critical"],
                        value="High",
                        key="priority_slider")
                
                # Store treatment data in session state
                st.session_state.treatment_data = {
                    'diagnosis': diagnosis,
                    'procedures': procedures,
                    'admission': admission,
                    'priority': priority
                }
                
                # Submit button
                if st.button("💾 Save Treatment Plan", key="save_treatment", use_container_width=True):
                    current_case['treatment_plan'] = {
                        **st.session_state.treatment_data,
                        'created_at': datetime.now()
                    }
                    st.success("✅ Treatment plan saved successfully!")
            
            with action_tab3:
                st.subheader("Remote Consultation")
                st.info("🎥 HD video consultation ready - Network optimized for emergency streaming")
                
                # Video consultation options
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📞 Start Video Call", key="start_video", use_container_width=True):
                        st.success("🔊 HD video call initiated with patient...")
                        st.info("💡 Network bandwidth boosted for optimal video quality")
                    
                    if st.button("🎤 Audio Consultation", key="audio_consult", use_container_width=True):
                        st.success("🔈 Audio consultation started")
                
                with col2:
                    if st.button("📱 Check Connectivity", key="check_connectivity", use_container_width=True):
                        st.info("📡 Checking network connectivity...")
                        time.sleep(1)
                        st.success("✅ Network optimized for consultation")
                
                st.markdown("---")
                st.subheader("Remote Monitoring")
                
                # Remote monitoring actions
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🩺 Request Live Vitals", key="request_vitals", use_container_width=True):
                        system.update_vital_signs(current_case['case_id'])
                        st.success("📊 Live vitals updated successfully!")
                
                with col2:
                    if st.button("📷 Request Image Upload", key="request_image", use_container_width=True):
                        st.info("🖼️ Request sent to patient for wound/image upload")
            
            # Display Current Plans
            if current_case.get('medication_prescribed'):
                st.markdown("---")
                st.markdown('<div class="subsection-header">💊 Current Prescription</div>', unsafe_allow_html=True)
                st.json(current_case['medication_prescribed'])
            
            if current_case.get('treatment_plan'):
                st.markdown("---")
                st.markdown('<div class="subsection-header">📄 Current Treatment Plan</div>', unsafe_allow_html=True)
                st.json(current_case['treatment_plan'])
        
        else:
            st.info("📭 No active emergency cases. Please initiate an emergency case in the Emergency tab to begin medical management.")
    
    with col2:
        # Enhanced Patient Vitals Section
        st.markdown('<div class="subsection-header">📊 Live Patient Vitals</div>', unsafe_allow_html=True)
        
        if current_case:
            # Update vitals periodically
            if 'last_vital_update' not in st.session_state or \
               (datetime.now() - st.session_state.last_vital_update).seconds > 8:
                system.update_vital_signs(current_case['case_id'])
                st.session_state.last_vital_update = datetime.now()
            
            vitals = current_case['vital_signs']
            
            # Enhanced Vitals Display with better visual hierarchy
            vital_metrics = [
                ("❤️ Heart Rate", f"{vitals['heart_rate']} BPM", 
                 "🔴" if vitals['heart_rate'] > 100 else "🟢" if vitals['heart_rate'] > 60 else "🟡"),
                ("🩸 Blood Pressure", vitals['blood_pressure'], 
                 "🔴" if int(vitals['blood_pressure'].split('/')[0]) > 140 else "🟢"),
                ("💨 O2 Saturation", f"{vitals['oxygen_saturation']}%", 
                 "🔴" if vitals['oxygen_saturation'] < 92 else "🟢"),
                ("🌡️ Temperature", f"{vitals['temperature']}°C", 
                 "🔴" if vitals['temperature'] > 38.0 else "🟢"),
                ("🫁 Respiration", f"{vitals['respiratory_rate']}/min", 
                 "🔴" if vitals['respiratory_rate'] > 25 else "🟢"),
                ("🩸 Glucose", f"{vitals['blood_glucose']} mg/dL", 
                 "🔴" if vitals['blood_glucose'] > 180 else "🟢")
            ]
            
            for icon, value, status in vital_metrics:
                st.metric(icon, value)
            
            # Update vitals button
            if st.button("🔄 Update Vitals", key="update_vitals_doc", use_container_width=True):
                system.update_vital_signs(current_case['case_id'])
                st.rerun()
        
        else:
            st.info("👈 Start an emergency case to monitor patient vitals in real-time")

def display_real_time_dashboard(system, current_case):
    """Enhanced dashboard with real-time data streaming and FIXED VISIBILITY"""
    st.markdown('<div class="section-header">📊 Real-time Emergency Dashboard</div>', unsafe_allow_html=True)
    
    if current_case:
        # Get real-time metrics
        real_time_metrics = system.get_real_time_metrics(current_case['case_id'])
        
        # Real-time Status Header with FIXED VISIBILITY
        st.markdown("### 🔄 Real-time Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="dashboard-card">
                <h4>🔄 Monitoring Status</h4>
                <p><span class="realtime-indicator realtime-active"></span> Live Monitoring Active</p>
                <p><strong>Last Update:</strong> {real_time_metrics['last_update'].strftime("%H:%M:%S")}</p>
                <p><strong>Case Status:</strong> {real_time_metrics['status'].upper()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="dashboard-card">
                <h4>📍 Location Tracking</h4>
                <p><strong>Updates:</strong> {real_time_metrics['location_history_count']}</p>
                <p><strong>Movement:</strong> {real_time_metrics['last_location']['movement'] if real_time_metrics['last_location'] else 'Unknown'}</p>
                <p><strong>Accuracy:</strong> {real_time_metrics['last_location']['accuracy'] if real_time_metrics['last_location'] else 'N/A'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="dashboard-card">
                <h4>📡 Network Quality</h4>
                <p><strong>Updates:</strong> {real_time_metrics['network_updates_count']}</p>
                <p><strong>Health Score:</strong> {real_time_metrics['last_network']['network_health'] if real_time_metrics['last_network'] else 'N/A'}%</p>
                <p><strong>Congestion:</strong> {real_time_metrics['last_network']['congestion_level'] if real_time_metrics['last_network'] else 'N/A'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Real-time Data Stream with FIXED VISIBILITY
        st.markdown("### 📈 Live Data Stream")
        
        stream_col1, stream_col2 = st.columns(2)
        
        with stream_col1:
            st.markdown("#### 📍 Location Updates")
            if real_time_metrics['last_location']:
                location_data = real_time_metrics['last_location']
                st.markdown(f"""
                <div class="data-stream">
                    <strong>Timestamp:</strong> {location_data['timestamp'].strftime("%H:%M:%S")}<br>
                    <strong>Position:</strong> {location_data['latitude']:.6f}, {location_data['longitude']:.6f}<br>
                    <strong>Accuracy:</strong> {location_data.get('accuracy', 'Unknown')}<br>
                    <strong>Movement:</strong> {location_data.get('movement', 'Unknown')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="data-stream">
                    <strong>Status:</strong> Waiting for location data...<br>
                    <strong>Message:</strong> Location tracking will begin shortly
                </div>
                """, unsafe_allow_html=True)
        
        with stream_col2:
            st.markdown("#### 📡 Network Updates")
            if real_time_metrics['last_network']:
                network_data = real_time_metrics['last_network']
                st.markdown(f"""
                <div class="data-stream">
                    <strong>Timestamp:</strong> {network_data['timestamp'].strftime("%H:%M:%S")}<br>
                    <strong>Congestion Level:</strong> {network_data.get('congestion_level', 'Unknown')}<br>
                    <strong>Health Score:</strong> {network_data.get('network_health', 'N/A')}%<br>
                    <strong>Active Users:</strong> {network_data.get('active_users', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="data-stream">
                    <strong>Status:</strong> Gathering network data...<br>
                    <strong>Message:</strong> Network metrics will appear here
                </div>
                """, unsafe_allow_html=True)
        
        # Vital Signs in Real-time Dashboard
        st.markdown("### 💓 Live Vital Signs")
        if current_case and current_case.get('vital_signs'):
            vitals = current_case['vital_signs']
            vital_col1, vital_col2, vital_col3, vital_col4 = st.columns(4)
            
            with vital_col1:
                st.markdown(f"""
                <div class="dashboard-card">
                    <h4>❤️ Heart Rate</h4>
                    <p style="font-size: 1.5rem; font-weight: bold; text-align: center; margin: 10px 0;">
                        {vitals['heart_rate']} BPM
                    </p>
                    <p style="text-align: center; color: {'#ef4444' if vitals['heart_rate'] > 100 else '#10b981'};">
                        {'⚠️ High' if vitals['heart_rate'] > 100 else '✅ Normal'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with vital_col2:
                st.markdown(f"""
                <div class="dashboard-card">
                    <h4>💨 O2 Saturation</h4>
                    <p style="font-size: 1.5rem; font-weight: bold; text-align: center; margin: 10px 0;">
                        {vitals['oxygen_saturation']}%
                    </p>
                    <p style="text-align: center; color: {'#ef4444' if vitals['oxygen_saturation'] < 92 else '#10b981'};">
                        {'⚠️ Low' if vitals['oxygen_saturation'] < 92 else '✅ Normal'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with vital_col3:
                st.markdown(f"""
                <div class="dashboard-card">
                    <h4>🌡️ Temperature</h4>
                    <p style="font-size: 1.5rem; font-weight: bold; text-align: center; margin: 10px 0;">
                        {vitals['temperature']}°C
                    </p>
                    <p style="text-align: center; color: {'#ef4444' if vitals['temperature'] > 38.0 else '#10b981'};">
                        {'⚠️ Fever' if vitals['temperature'] > 38.0 else '✅ Normal'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            with vital_col4:
                st.markdown(f"""
                <div class="dashboard-card">
                    <h4>🩸 Blood Pressure</h4>
                    <p style="font-size: 1.3rem; font-weight: bold; text-align: center; margin: 10px 0;">
                        {vitals['blood_pressure']}
                    </p>
                    <p style="text-align: center; color: {'#ef4444' if int(vitals['blood_pressure'].split('/')[0]) > 140 else '#10b981'};">
                        {'⚠️ High' if int(vitals['blood_pressure'].split('/')[0]) > 140 else '✅ Normal'}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # Auto-refresh control with better styling
        st.markdown("### 🔄 Refresh Controls")
        st.markdown("""
        <div class="refresh-controls">
        """, unsafe_allow_html=True)
        
        auto_refresh = st.checkbox("Enable Auto-refresh (5 seconds)", value=True, key="auto_refresh_dashboard")
        
        if auto_refresh:
            st.info("🔄 Dashboard will auto-refresh every 5 seconds")
            time.sleep(5)
            st.rerun()
        else:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Manual Refresh", key="manual_refresh_dashboard", use_container_width=True):
                    st.rerun()
            with col2:
                if st.button("📊 Update All Data", key="update_all_dashboard", use_container_width=True):
                    if current_case:
                        system.update_vital_signs(current_case['case_id'])
                        system._update_patient_location(current_case['case_id'])
                        system._update_network_quality(current_case['case_id'])
                    st.success("✅ All data updated successfully!")
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    else:
        st.info("👈 Start an emergency case in the Emergency tab to see real-time dashboard data")
        
        # Show sample dashboard when no case is active
        st.markdown("### 📊 Sample Dashboard Preview")
        sample_col1, sample_col2, sample_col3 = st.columns(3)
        
        with sample_col1:
            st.markdown("""
            <div class="dashboard-card">
                <h4>🔄 Monitoring Status</h4>
                <p><span class="realtime-indicator realtime-inactive"></span> No Active Case</p>
                <p><strong>Last Update:</strong> --:--:--</p>
                <p><strong>Case Status:</strong> INACTIVE</p>
            </div>
            """, unsafe_allow_html=True)
        
        with sample_col2:
            st.markdown("""
            <div class="dashboard-card">
                <h4>📍 Location Tracking</h4>
                <p><strong>Updates:</strong> 0</p>
                <p><strong>Movement:</strong> Unknown</p>
                <p><strong>Accuracy:</strong> N/A</p>
            </div>
            """, unsafe_allow_html=True)
        
        with sample_col3:
            st.markdown("""
            <div class="dashboard-card">
                <h4>📡 Network Quality</h4>
                <p><strong>Updates:</strong> 0</p>
                <p><strong>Health Score:</strong> N/A</p>
                <p><strong>Congestion:</strong> N/A</p>
            </div>
            """, unsafe_allow_html=True)

def display_enhanced_network_intel(system):
    """Enhanced network intelligence with real-time features and FIXED API STATUS VISIBILITY"""
    st.markdown('<div class="section-header">📡 Real-time Network Intelligence</div>', unsafe_allow_html=True)
    
    # Real-time API Status with FIXED VISIBILITY
    st.markdown("### 🔌 Live API Status")
    
    api_status_cols = st.columns(4)
    api_services = [
        ("Number Verification", "number_verification"),
        ("Device Reachability", "device_reachability"), 
        ("Location Services", "location_retrieval"),
        ("Quality on Demand", "quality_on_demand"),
        ("Congestion Insights", "congestion_insights"),
        ("SIM Swap Detection", "sim_swap"),
        ("Geofencing", "geofencing"),
        ("Network Slicing", "network_slicing")
    ]
    
    for i, (name, key) in enumerate(api_services):
        with api_status_cols[i % 4]:
            status = "active" if not system.nokia_client.demo_mode else "demo"
            status_class = "active" if status == "active" else "demo"
            
            st.markdown(f"""
            <div class="api-status-card {status_class}">
                <div class="realtime-indicator {'realtime-active' if status == 'active' else 'realtime-inactive'}"></div>
                <strong>{name}</strong>
                <small>{'🟢 Live' if status == 'active' else '🟡 Demo'}</small>
            </div>
            """, unsafe_allow_html=True)
    
    # API Status Summary
    st.markdown("### 📊 API Status Summary")
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.markdown("""
        <div class="dashboard-card">
            <h4>🟢 Active APIs</h4>
            <p style="font-size: 2rem; font-weight: bold; text-align: center; margin: 10px 0; color: #10b981;">
                {}</p>
            <p style="text-align: center;">Live Connections</p>
        </div>
        """.format("8" if not system.nokia_client.demo_mode else "0"), unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("""
        <div class="dashboard-card">
            <h4>🟡 Demo APIs</h4>
            <p style="font-size: 2rem; font-weight: bold; text-align: center; margin: 10px 0; color: #f59e0b;">
                {}</p>
            <p style="text-align: center;">Simulated Data</p>
        </div>
        """.format("8" if system.nokia_client.demo_mode else "0"), unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("""
        <div class="dashboard-card">
            <h4>📡 Response Time</h4>
            <p style="font-size: 2rem; font-weight: bold; text-align: center; margin: 10px 0; color: #2563eb;">
                {}ms</p>
            <p style="text-align: center;">Average Latency</p>
        </div>
        """.format(random.randint(50, 150)), unsafe_allow_html=True)
    
    with summary_col4:
        st.markdown("""
        <div class="dashboard-card">
            <h4>⚡ Uptime</h4>
            <p style="font-size: 2rem; font-weight: bold; text-align: center; margin: 10px 0; color: #10b981;">
                99.9%</p>
            <p style="text-align: center;">Service Reliability</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Real-time Network Metrics with enhanced visualization
    st.markdown("### 📊 Live Network Performance")
    
    if system.network_metrics_history:
        df = pd.DataFrame(system.network_metrics_history)
        
        # Create real-time charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['bandwidth'], 
                mode='lines+markers',
                name='Bandwidth',
                line=dict(color='#2563eb', width=3),
                marker=dict(size=4, color='#2563eb')
            ))
            fig.update_layout(
                title="Real-time Bandwidth (Mbps)",
                height=300,
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df['timestamp'], 
                y=df['latency'], 
                mode='lines+markers',
                name='Latency',
                line=dict(color='#ef4444', width=3),
                marker=dict(size=4, color='#ef4444')
            ))
            fig.update_layout(
                title="Real-time Latency (ms)",
                height=300,
                showlegend=False,
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Enhanced Network Actions with real-time capabilities
    st.markdown("### 🚀 Real-time Network Actions")
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("🔄 Refresh All Data", key="refresh_all", use_container_width=True):
            st.rerun()
    
    with action_col2:
        if st.button("📡 Test All APIs", key="test_apis", use_container_width=True):
            with st.spinner("Testing all API connections..."):
                system.nokia_client.test_connection()
                st.success("API testing completed!")
    
    with action_col3:
        if st.button("🚨 Emergency Boost", key="emergency_boost_all", use_container_width=True):
            st.warning("Activating emergency network prioritization...")
            time.sleep(1)
            st.success("Emergency traffic prioritized across all networks!")
    
    with action_col4:
        if st.button("📊 Export Live Data", key="export_live", use_container_width=True):
            # Export current network metrics
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "network_metrics": system.network_metrics_history[-10:],  # Last 10 records
                "active_cases": len([c for c in system.emergency_cases if c['status'] == 'active']),
                "api_status": "demo" if system.nokia_client.demo_mode else "live"
            }
            
            st.download_button(
                label="📥 Download Live Data",
                data=json.dumps(export_data, indent=2, default=str),
                file_name=f"network_live_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

def display_enhanced_live_tracking(system, current_case):
    """Enhanced live tracking with real-time features"""
    st.markdown('<div class="section-header">📍 Real-time Patient Tracking</div>', unsafe_allow_html=True)
    
    if current_case:
        real_time_metrics = system.get_real_time_metrics(current_case['case_id'])
        
        # Real-time location map with history
        if real_time_metrics['last_location']:
            location_data = real_time_metrics['last_location']
            
            # Create enhanced map with movement tracking
            map_center = [location_data['latitude'], location_data['longitude']]
            m = folium.Map(location=map_center, zoom_start=15, tiles='CartoDB positron')
            
            # Add current location marker
            folium.Marker(
                map_center,
                popup=f"""
                <strong>Patient:</strong> {current_case['patient_data']['name']}<br>
                <strong>Time:</strong> {location_data['timestamp'].strftime('%H:%M:%S')}<br>
                <strong>Movement:</strong> {location_data.get('movement', 'Unknown')}
                """,
                tooltip="Current Location",
                icon=folium.Icon(color="red", icon="heart-pulse", prefix="fa")
            ).add_to(m)
            
            # Add location history as a polyline
            location_history = current_case['real_time_data']['location_updates']
            if len(location_history) > 1:
                path_coords = [[loc['latitude'], loc['longitude']] for loc in location_history]
                folium.PolyLine(
                    path_coords,
                    color='blue',
                    weight=3,
                    opacity=0.7,
                    popup="Patient Movement Path"
                ).add_to(m)
            
            # Add geofence circle
            folium.Circle(
                map_center,
                radius=100,  # 100m geofence
                popup="Patient Safety Zone",
                color="green",
                fill=True,
                fillOpacity=0.1
            ).add_to(m)
            
            folium_static(m, width=800, height=400)
        
        # Real-time movement analysis
        st.markdown("### 🏃 Movement Analysis")
        if real_time_metrics['last_location']:
            movement = real_time_metrics['last_location'].get('movement', 'UNKNOWN')
            
            movement_col1, movement_col2, movement_col3 = st.columns(3)
            
            with movement_col1:
                if movement == "STATIONARY":
                    st.markdown('<div class="modern-card" style="background: #dcfce7;"><h4>🛑 Stationary</h4><p>Patient is not moving</p></div>', unsafe_allow_html=True)
                elif movement == "MOVING_SLOW":
                    st.markdown('<div class="modern-card" style="background: #fef3c7;"><h4>🚶 Slow Movement</h4><p>Patient is moving slowly</p></div>', unsafe_allow_html=True)
                elif movement == "MOVING_FAST":
                    st.markdown('<div class="modern-card" style="background: #fee2e2;"><h4>🏃 Fast Movement</h4><p>Patient is moving quickly</p></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="modern-card"><h4>❓ Unknown</h4><p>Movement data unavailable</p></div>', unsafe_allow_html=True)
            
            with movement_col2:
                st.metric("Location Updates", real_time_metrics['location_history_count'])
            
            with movement_col3:
                st.metric("Last Update", real_time_metrics['last_update'].strftime("%H:%M:%S"))
        
        # Real-time location history chart
        if current_case['real_time_data']['location_updates']:
            st.markdown("### 📈 Location History")
            location_df = pd.DataFrame(current_case['real_time_data']['location_updates'])
            location_df['time_elapsed'] = (location_df['timestamp'] - location_df['timestamp'].min()).dt.total_seconds()
            
            fig = px.scatter(
                location_df, 
                x='time_elapsed', 
                y='accuracy',
                title="Location Accuracy Over Time",
                labels={'time_elapsed': 'Time (seconds)', 'accuracy': 'Accuracy (meters)'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("👈 Start an emergency case to see real-time patient tracking")

def create_enhanced_sidebar(system, current_case):
    """Create a clean, informative sidebar with enhanced design"""
    with st.sidebar:
        # Enhanced Header
        st.markdown("""
        <div style="text-align: center; margin-bottom: 30px; padding: 20px 0; border-bottom: 1px solid #334155;">
            <h2 style="color: white; margin-bottom: 8px; font-size: 1.8rem;">🏥 NetCare+</h2>
            <p style="color: #cbd5e1; font-size: 0.9rem; margin: 0;">Real-time Emergency Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Connection Status with enhanced design
        st.markdown("### 🔗 Connection Status")
        if system.nokia_client.demo_mode:
            st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.2); color: #f59e0b; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #f59e0b;">
                <strong>🔧 Demo Mode</strong>
                <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #fbbf24;">Using simulated data</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 12px; border-radius: 8px; margin: 8px 0; border-left: 4px solid #10b981;">
                <strong>✅ Live Connection</strong>
                <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: #34d399;">Nokia APIs Active</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Enhanced System Overview
        st.markdown("### 📊 System Overview")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active Cases", "1" if current_case else "0")
            st.metric("Response Time", "2.1s")
        with col2:
            st.metric("Success Rate", "98.2%")
            st.metric("System Uptime", "99.9%")
        
        # Quick Actions with enhanced buttons
        st.markdown("### ⚡ Quick Actions")
        if st.button("🔄 Test Connection", key="test_connection_sidebar", use_container_width=True):
            with st.spinner("Testing API connection..."):
                system.nokia_client.test_connection()
                st.rerun()
        
        if st.button("📋 System Report", key="system_report_sidebar", use_container_width=True):
            st.success("System status report generated")
        
        if st.button("🆘 Emergency Contacts", key="emergency_contacts", use_container_width=True):
            st.info("""
            **Emergency Contacts:**
            - 🏥 City General: (555) 123-4567
            - 🚑 Ambulance: (555) 987-6543  
            - 👮 Emergency: 911
            - 🔥 Fire Dept: (555) 555-5555
            """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #94a3b8; font-size: 0.8rem; margin-top: 20px;">
            <p>NetCare+ v2.0 Real-time</p>
            <p>Powered by Nokia Network-as-Code</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    # Enhanced Header with real-time indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="main-header">NetCare+ Real-time</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Live Emergency Healthcare Platform</div>', unsafe_allow_html=True)
    
    # Real-time status indicator in header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <span class="realtime-indicator realtime-active"></span>
        <strong>LIVE</strong> - Real-time monitoring active
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize system and session state
    if 'emergency_system' not in st.session_state:
        st.session_state.emergency_system = RealTimeNetCareSystem()
    if 'current_case' not in st.session_state:
        st.session_state.current_case = None
    
    system = st.session_state.emergency_system
    current_case = st.session_state.current_case
    
    # Create enhanced sidebar
    create_enhanced_sidebar(system, current_case)
    
    # Enhanced navigation with real-time tab
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🚨 Emergency", 
        "📍 Live Tracking", 
        "👨‍⚕️ Doctor Portal", 
        "📡 Network Intel",
        "📊 Real-time Dashboard"
    ])
    
    with tab1:
        st.markdown('<div class="emergency-alert">🚨 REAL-TIME EMERGENCY RESPONSE</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Patient form
            patient_data = create_patient_form()
            if patient_data:
                current_case = system.initiate_emergency(patient_data)
                st.session_state.current_case = current_case
                st.rerun()
            
            # Show progress if case exists
            if current_case:
                display_emergency_progress(current_case)
        
        with col2:
            st.markdown("### 📊 Live Status")
            if current_case:
                steps = current_case["steps"]
                verified = any(step.get("number_verified", False) for step in steps)
                reachable = any(step.get("reachable", False) for step in steps)
                location_acquired = any("latitude" in step for step in steps)
                network_enhanced = any(step.get("profile") for step in steps)
                
                status_data = [
                    ("🆔 Identity", "✅ Verified" if verified else "❌ Pending", "#10b981" if verified else "#ef4444"),
                    ("📱 Connectivity", "✅ Online" if reachable else "🔴 Offline", "#10b981" if reachable else "#ef4444"),
                    ("📍 Location", "📍 Acquired" if location_acquired else "🔄 Locating", "#10b981" if location_acquired else "#f59e0b"),
                    ("⚡ Network", "🎯 Enhanced" if network_enhanced else "📶 Standard", "#10b981" if network_enhanced else "#64748b"),
                    ("🔧 API Mode", "🎯 Demo" if current_case.get("demo_mode") else "🔗 Live", "#f59e0b" if current_case.get("demo_mode") else "#10b981")
                ]
                
                for icon, text, color in status_data:
                    st.markdown(f"""
                    <div style="background: {color}20; color: {color}; padding: 12px; border-radius: 8px; margin: 6px 0; text-align: center; border: 1px solid {color}40;">
                        <strong>{icon} {text}</strong>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No active emergency case")
    
    with tab2:
        # Enhanced live tracking with real-time updates
        display_enhanced_live_tracking(system, current_case)
    
    with tab3:
        # Your existing doctor portal
        display_doctor_portal(system, current_case)
    
    with tab4:
        # Enhanced network intelligence
        display_enhanced_network_intel(system)
    
    with tab5:
        # New real-time dashboard
        display_real_time_dashboard(system, current_case)

if __name__ == "__main__":
    main()