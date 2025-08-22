import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, Tuple, List
import os
from pathlib import Path

class MLModelService:
    """Service for integrating ML models with the pension AI system"""
    
    def _init_(self):
        self.risk_model = None
        self.fraud_model = None
        self.models_loaded = False
        self.load_models()
    
    def load_models(self):
        """Load the ML models from the uploaded files"""
        try:
            # Get the workspace root directory (parent of server directory)
            workspace_root = Path(_file_).parent.parent.parent
            
            # Load risk model
            risk_model_path = workspace_root / "risk_final_model.joblib"
            if risk_model_path.exists():
                self.risk_model = joblib.load(risk_model_path)
                print(f"✅ Risk model loaded successfully from {risk_model_path}")
            else:
                print(f"⚠ Risk model not found at {risk_model_path}")
            
            # Load fraud model
            fraud_model_path = workspace_root / "fraud_final_model.joblib"
            if fraud_model_path.exists():
                self.fraud_model = joblib.load(fraud_model_path)
                print(f"✅ Fraud model loaded successfully from {fraud_model_path}")
            else:
                print(f"⚠ Fraud model not found at {fraud_model_path}")
            
            self.models_loaded = bool(self.risk_model and self.fraud_model)
            
        except Exception as e:
            print(f"❌ Error loading ML models: {e}")
            self.models_loaded = False
    
    def prepare_risk_features(self, user_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for risk analysis model"""
        try:
            # Check if we have the training columns from the model
            if hasattr(self.risk_model, 'training_columns') and self.risk_model.get('training_columns'):
                training_columns = self.risk_model['training_columns']
                print(f"🔍 Using {len(training_columns)} training columns from model")
                
                # Create feature vector with expected columns
                features = []
                for col in training_columns:
                    if col in user_data:
                        features.append(user_data[col])
                    else:
                        # Use default values for missing columns
                        if 'income' in col.lower() or 'salary' in col.lower():
                            features.append(75000)  # Default income
                        elif 'debt' in col.lower():
                            features.append(25000)  # Default debt
                        elif 'risk' in col.lower():
                            features.append(0.5)  # Default risk tolerance
                        elif 'volatility' in col.lower():
                            features.append(0.5)  # Default volatility
                        elif 'diversity' in col.lower():
                            features.append(0.5)  # Default diversity
                        elif 'health' in col.lower():
                            features.append(0.67)  # Default health
                        else:
                            features.append(0.0)  # Default for unknown columns
                
                # Ensure we have the right number of features
                if len(features) != 67:
                    print(f"⚠ Feature count mismatch: expected 67, got {len(features)}")
                    # Pad or truncate to match expected count
                    while len(features) < 67:
                        features.append(0.0)
                    features = features[:67]
                
                return np.array(features).reshape(1, -1)
            
            else:
                # Fallback to simple feature preparation
                print("⚠ No training columns found, using fallback feature preparation")
                features = [0.5] * 67  # Create 67 default features
                return np.array(features).reshape(1, -1)
            
        except Exception as e:
            print(f"❌ Error preparing risk features: {e}")
            # Return default features if error occurs
            features = [0.5] * 67
            return np.array(features).reshape(1, -1)
    
    def prepare_fraud_features(self, user_data: Dict[str, Any]) -> np.ndarray:
        """Prepare features for fraud detection model"""
        try:
            # Check if we have the training columns from the model
            if hasattr(self.fraud_model, 'training_columns') and self.fraud_model.get('training_columns'):
                training_columns = self.fraud_model['training_columns']
                print(f"🔍 Using {len(training_columns)} training columns from fraud model")
                
                # Create feature vector with expected columns
                features = []
                for col in training_columns:
                    if col in user_data:
                        features.append(user_data[col])
                    else:
                        # Use default values for missing columns
                        if 'income' in col.lower() or 'salary' in col.lower():
                            features.append(75000)  # Default income
                        elif 'debt' in col.lower():
                            features.append(25000)  # Default debt
                        elif 'risk' in col.lower():
                            features.append(0.5)  # Default risk tolerance
                        elif 'volatility' in col.lower():
                            features.append(0.5)  # Default volatility
                        elif 'diversity' in col.lower():
                            features.append(0.5)  # Default diversity
                        elif 'health' in col.lower():
                            features.append(0.67)  # Default health
                        else:
                            features.append(0.0)  # Default for unknown columns
                
                # Ensure we have the right number of features
                if len(features) != 69:
                    print(f"⚠ Feature count mismatch: expected 69, got {len(features)}")
                    # Pad or truncate to match expected count
                    while len(features) < 69:
                        features.append(0.0)
                    features = features[:69]
                
                return np.array(features).reshape(1, -1)
            
            else:
                # Fallback to simple feature preparation
                print("⚠ No training columns found, using fallback feature preparation")
                features = [0.5] * 69  # Create 69 default features
                return np.array(features).reshape(1, -1)
            
        except Exception as e:
            print(f"❌ Error preparing fraud features: {e}")
            # Return default features if error occurs
            features = [0.5] * 69
            return np.array(features).reshape(1, -1)
    
    def predict_risk(self, user_data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """Predict risk using ML model, fallback to default if model fails"""
        try:
            if not self.risk_model or not self.models_loaded:
                print("⚠ Risk model not available, using fallback")
                return self._fallback_risk_analysis(user_data), False
            
            # Check if model is a dictionary with actual model inside
            if isinstance(self.risk_model, dict) and 'model' in self.risk_model:
                actual_model = self.risk_model['model']
                print("🔍 Using model from dictionary structure")
            else:
                actual_model = self.risk_model
            
            # Prepare features for ML model
            features = self.prepare_risk_features(user_data)
            
            # Make prediction
            prediction = actual_model.predict(features)[0]
            prediction_proba = actual_model.predict_proba(features)[0] if hasattr(actual_model, 'predict_proba') else None
            
            # Convert prediction to risk level
            if prediction == 0:
                risk_level = "Low"
                risk_score = 0.2
            elif prediction == 1:
                risk_level = "Medium"
                risk_score = 0.5
            else:
                risk_level = "High"
                risk_score = 0.8
            
            result = {
                "risk_level": risk_level,
                "risk_score": float(risk_score),
                "confidence": float(max(prediction_proba)) if prediction_proba else 0.8,
                "ml_model_used": True,
                "analysis_method": "ML Model Prediction",
                "factors_considered": list(user_data.keys()),
                "recommendations": self._get_risk_recommendations(risk_level, user_data)
            }
            
            print(f"✅ ML Risk Model Prediction: {risk_level} (Score: {risk_score:.2f})")
            return result, True
            
        except Exception as e:
            print(f"❌ ML Risk Model Error: {e}, using fallback")
            return self._fallback_risk_analysis(user_data), False
    
    def predict_fraud(self, user_data: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
        """Predict fraud using ML model, fallback to default if model fails"""
        try:
            if not self.fraud_model or not self.models_loaded:
                print("⚠ Fraud model not available, using fallback")
                return self._fallback_fraud_detection(user_data), False
            
            # Check if model is a dictionary with actual model inside
            if isinstance(self.fraud_model, dict) and 'model' in self.fraud_model:
                actual_model = self.fraud_model['model']
                print("🔍 Using fraud model from dictionary structure")
            else:
                actual_model = self.fraud_model
            
            # Prepare features for ML model
            features = self.prepare_fraud_features(user_data)
            
            # Make prediction
            prediction = actual_model.predict(features)[0]
            prediction_proba = actual_model.predict_proba(features)[0] if hasattr(actual_model, 'predict_proba') else None
            
            # Convert prediction to fraud risk
            if prediction == 0:
                fraud_risk = "Low"
                anomaly_score = 0.2
            else:
                fraud_risk = "High"
                anomaly_score = 0.8
            
            result = {
                "fraud_risk": fraud_risk,
                "anomaly_score": float(anomaly_score),
                "confidence": float(max(prediction_proba)) if prediction_proba else 0.8,
                "ml_model_used": True,
                "analysis_method": "ML Model Prediction",
                "suspicious_indicators": self._get_fraud_indicators(user_data, fraud_risk),
                "recommendations": self._get_fraud_recommendations(fraud_risk)
            }
            
            print(f"✅ ML Fraud Model Prediction: {fraud_risk} (Score: {anomaly_score:.2f})")
            return result, True
            
        except Exception as e:
            print(f"❌ ML Fraud Model Error: {e}, using fallback")
            return self._fallback_fraud_detection(user_data), False
    
    def _fallback_risk_analysis(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback risk analysis when ML model is not available"""
        print("🔄 Using fallback risk analysis")
        
        # Simple rule-based risk assessment
        risk_score = 0.5
        risk_level = "Medium"
        
        # Adjust based on data
        if user_data.get('Debt_Level', 0) > user_data.get('Annual_Income', 1) * 0.5:
            risk_score += 0.2
        if user_data.get('Volatility', 0.5) > 0.7:
            risk_score += 0.15
        if user_data.get('Portfolio_Diversity_Score', 0.5) < 0.3:
            risk_score += 0.1
        
        # Cap risk score
        risk_score = min(risk_score, 1.0)
        
        if risk_score < 0.4:
            risk_level = "Low"
        elif risk_score > 0.7:
            risk_level = "High"
        
        return {
            "risk_level": risk_level,
            "risk_score": float(risk_score),
            "confidence": 0.6,
            "ml_model_used": False,
            "analysis_method": "Rule-based Fallback",
            "factors_considered": list(user_data.keys()),
            "recommendations": self._get_risk_recommendations(risk_level, user_data)
        }
    
    def _fallback_fraud_detection(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback fraud detection when ML model is not available"""
        print("🔄 Using fallback fraud detection")
        
        # Simple rule-based fraud detection
        anomaly_score = 0.3
        fraud_risk = "Low"
        
        # Check for suspicious patterns
        if user_data.get('Debt_Level', 0) > user_data.get('Annual_Income', 1) * 2:
            anomaly_score += 0.3
        if user_data.get('Volatility', 0.5) > 0.8:
            anomaly_score += 0.2
        if user_data.get('Portfolio_Diversity_Score', 0.5) < 0.2:
            anomaly_score += 0.2
        
        # Cap anomaly score
        anomaly_score = min(anomaly_score, 1.0)
        
        if anomaly_score > 0.6:
            fraud_risk = "High"
        
        return {
            "fraud_risk": fraud_risk,
            "anomaly_score": float(anomaly_score),
            "confidence": 0.5,
            "ml_model_used": False,
            "analysis_method": "Rule-based Fallback",
            "suspicious_indicators": self._get_fraud_indicators(user_data, fraud_risk),
            "recommendations": self._get_fraud_recommendations(fraud_risk)
        }
    
    def _get_risk_recommendations(self, risk_level: str, user_data: Dict[str, Any]) -> List[str]:
        """Get risk-specific recommendations"""
        recommendations = []
        
        if risk_level == "High":
            recommendations.extend([
                "Consider reducing debt levels to improve financial stability",
                "Diversify portfolio to reduce concentration risk",
                "Review and potentially adjust risk tolerance settings",
                "Consider consulting with a financial advisor"
            ])
        elif risk_level == "Medium":
            recommendations.extend([
                "Monitor portfolio performance regularly",
                "Consider gradual portfolio diversification",
                "Review debt-to-income ratio periodically"
            ])
        else:  # Low risk
            recommendations.extend([
                "Maintain current conservative approach",
                "Consider slightly increasing risk for potential higher returns",
                "Continue regular portfolio monitoring"
            ])
        
        return recommendations
    
    def _get_fraud_indicators(self, user_data: Dict[str, Any], fraud_risk: str) -> List[str]:
        """Get fraud risk indicators"""
        indicators = []
        
        if fraud_risk == "High":
            if user_data.get('Debt_Level', 0) > user_data.get('Annual_Income', 1) * 2:
                indicators.append("Unusually high debt-to-income ratio")
            if user_data.get('Volatility', 0.5) > 0.8:
                indicators.append("Extremely high portfolio volatility")
            if user_data.get('Portfolio_Diversity_Score', 0.5) < 0.2:
                indicators.append("Very low portfolio diversity")
        
        return indicators
    
    def _get_fraud_recommendations(self, fraud_risk: str) -> List[str]:
        """Get fraud-specific recommendations"""
        if fraud_risk == "High":
            return [
                "Immediate review of all financial transactions",
                "Contact financial institution for account verification",
                "Consider freezing accounts temporarily",
                "Report suspicious activity to authorities if necessary"
            ]
        else:
            return [
                "Continue regular monitoring of account activity",
                "Report any unusual transactions immediately",
                "Maintain strong security practices"
            ]

# Global instance
ml_service = MLModelService()
