# Role-Based Endpoints for Pension AI API

## Overview

Based on your database structure, I've created specialized endpoints for each user role that provide appropriate data access and grouping. This ensures that advisors can only see their clients' data, regulators can see fraud-focused information, and residents can only access their own data.

## Database Structure

```
users table:
- id, full_name, email, password, role

pension_data table:
- id, user_id, age, gender, country, employment_status, annual_income, 
  current_savings, retirement_age_goal, risk_tolerance, contribution_amount, 
  contribution_frequency, employer_contribution, total_annual_contribution, 
  years_contributed, investment_type, fund_name, annual_return_rate, 
  volatility, fees_percentage, projected_pension_amount, expected_annual_payout, 
  inflation_adjusted_payout, years_of_payout, survivor_benefits, 
  transaction_id, transaction_amount, transaction_date, suspicious_flag, 
  anomaly_score, marital_status, number_of_dependents, education_level, 
  health_status, life_expectancy_estimate, home_ownership_status, debt_level, 
  monthly_expenses, savings_rate, investment_experience_level, financial_goals, 
  insurance_coverage, portfolio_diversity_score, tax_benefits_eligibility, 
  government_pension_eligibility, private_pension_eligibility, pension_type, 
  withdrawal_strategy, transaction_channel, ip_address, device_id, 
  geo_location, time_of_transaction, transaction_pattern_score, 
  previous_fraud_flag, account_age

advisor_clients table:
- id, advisor_id, resident_id
```

## Role-Based Endpoints

### 1. Resident Endpoints

#### GET /resident/dashboard
**Purpose**: Personal pension dashboard for residents
**Access**: Only users with role="resident"
**Returns**: Complete personal pension data including demographics, financial info, and risk indicators

**Response Structure**:
```json
{
  "user": {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "role": "resident"
  },
  "pension_data": {
    "age": 35,
    "gender": "Male",
    "country": "USA",
    "employment_status": "Full-time",
    "annual_income": 75000,
    "current_savings": 150000,
    "retirement_age_goal": 65,
    "risk_tolerance": "Medium",
    "contribution_amount": 5000,
    "employer_contribution": 3000,
    "total_annual_contribution": 8000,
    "years_contributed": 10,
    "projected_pension_amount": 450000,
    "expected_annual_payout": 18000,
    "portfolio_diversity_score": 0.7,
    "volatility": 0.15,
    "fraud_risk": "False",
    "anomaly_score": 0.2
  }
}
```

### 2. Advisor Endpoints

#### GET /advisor/dashboard
**Purpose**: Comprehensive dashboard showing all clients grouped by categories
**Access**: Only users with role="advisor"
**Returns**: Client data grouped by risk tolerance, age groups, and income levels

**Response Structure**:
```json
{
  "advisor_id": 101,
  "total_clients": 25,
  "grouped_data": {
    "by_risk_tolerance": {
      "Low": {
        "count": 8,
        "clients": [
          {
            "user_id": 201,
            "full_name": "Client Name",
            "age": 45,
            "annual_income": 60000,
            "current_savings": 120000,
            "risk_tolerance": "Low",
            "anomaly_score": 0.1
          }
        ]
      },
      "Medium": {
        "count": 12,
        "clients": [...]
      },
      "High": {
        "count": 5,
        "clients": [...]
      }
    },
    "by_age_group": {
      "30-39": {
        "count": 6,
        "clients": [...]
      },
      "40-49": {
        "count": 12,
        "clients": [...]
      }
    },
    "by_income_level": {
      "Low (<$50k)": {
        "count": 5,
        "clients": [...]
      },
      "Medium ($50k-$100k)": {
        "count": 15,
        "clients": [...]
      },
      "High (>$100k)": {
        "count": 5,
        "clients": [...]
      }
    }
  },
  "summary": {
    "total_clients": 25,
    "avg_age": 42.5,
    "avg_income": 68000,
    "avg_savings": 125000,
    "risk_distribution": {
      "Low": 8,
      "Medium": 12,
      "High": 5
    },
    "fraud_risk_summary": {
      "high": 2,
      "medium": 5,
      "low": 18
    }
  }
}
```

#### GET /advisor/client/{client_id}/details
**Purpose**: Detailed view of a specific client
**Access**: Only advisors can see their own clients
**Returns**: Comprehensive client information

**Response Structure**:
```json
{
  "client": {
    "id": 201,
    "full_name": "Client Name",
    "email": "client@example.com"
  },
  "pension_data": {
    "demographics": {
      "age": 45,
      "gender": "Female",
      "country": "USA",
      "employment_status": "Full-time",
      "marital_status": "Married",
      "number_of_dependents": 2,
      "education_level": "Bachelor's",
      "health_status": "Good"
    },
    "financial": {
      "annual_income": 60000,
      "current_savings": 120000,
      "debt_level": 15000,
      "monthly_expenses": 3500,
      "savings_rate": 0.15,
      "contribution_amount": 4000,
      "employer_contribution": 2000,
      "total_annual_contribution": 6000
    },
    "pension": {
      "retirement_age_goal": 65,
      "years_contributed": 8,
      "projected_pension_amount": 380000,
      "expected_annual_payout": 15200,
      "pension_type": "Defined Contribution"
    },
    "investment": {
      "risk_tolerance": "Low",
      "investment_type": "Conservative",
      "fund_name": "Vanguard Target 2045",
      "annual_return_rate": 0.06,
      "volatility": 0.12,
      "portfolio_diversity_score": 0.8
    },
    "risk_indicators": {
      "suspicious_flag": "False",
      "anomaly_score": 0.1,
      "transaction_amount": 3000,
      "transaction_date": "2024-01-15T10:30:00"
    }
  }
}
```

### 3. Regulator Endpoints

#### GET /regulator/dashboard
**Purpose**: Fraud-focused dashboard with risk analysis
**Access**: Only users with role="regulator"
**Returns**: All pension data grouped by fraud risk levels

**Response Structure**:
```json
{
  "total_users": 150,
  "fraud_analysis": {
    "high_risk_count": 12,
    "medium_risk_count": 28,
    "low_risk_count": 110,
    "total_suspicious": 8,
    "risk_groups": {
      "High Risk": {
        "count": 12,
        "users": [
          {
            "user_id": 301,
            "full_name": "User Name",
            "age": 38,
            "country": "USA",
            "annual_income": 85000,
            "anomaly_score": 0.95,
            "suspicious_flag": "True",
            "transaction_amount": 25000,
            "geo_location": "New York, NY",
            "ip_address": "192.168.1.100",
            "transaction_pattern_score": 0.88,
            "previous_fraud_flag": "True"
          }
        ]
      },
      "Medium Risk": {
        "count": 28,
        "users": [...]
      },
      "Low Risk": {
        "count": 110,
        "users": [...]
      }
    }
  },
  "risk_distribution": {
    "Low": 45,
    "Medium": 78,
    "High": 27
  },
  "geographic_analysis": {
    "New York, NY": {
      "count": 25,
      "high_risk": 3,
      "medium_risk": 8,
      "low_risk": 14,
      "total_anomaly_score": 12.5,
      "avg_anomaly_score": 0.5
    },
    "Los Angeles, CA": {
      "count": 20,
      "high_risk": 2,
      "medium_risk": 6,
      "low_risk": 12,
      "total_anomaly_score": 8.2,
      "avg_anomaly_score": 0.41
    }
  }
}
```

#### GET /regulator/user/{user_id}/details
**Purpose**: Detailed view of any user for compliance analysis
**Access**: Only users with role="regulator"
**Returns**: Complete user and pension data

**Response Structure**:
```json
{
  "user": {
    "id": 301,
    "full_name": "User Name",
    "email": "user@example.com",
    "role": "resident"
  },
  "pension_data": {
    "demographics": {
      "age": 38,
      "gender": "Male",
      "country": "USA",
      "employment_status": "Full-time",
      "marital_status": "Single",
      "number_of_dependents": 0,
      "education_level": "Master's",
      "health_status": "Excellent",
      "life_expectancy_estimate": 82
    },
    "financial": {
      "annual_income": 85000,
      "current_savings": 180000,
      "debt_level": 25000,
      "monthly_expenses": 4200,
      "savings_rate": 0.18,
      "contribution_amount": 6000,
      "employer_contribution": 3000,
      "total_annual_contribution": 9000
    },
    "pension": {
      "retirement_age_goal": 62,
      "years_contributed": 12,
      "projected_pension_amount": 520000,
      "expected_annual_payout": 20800,
      "pension_type": "Defined Contribution",
      "withdrawal_strategy": "Systematic"
    },
    "investment": {
      "risk_tolerance": "High",
      "investment_type": "Aggressive",
      "fund_name": "Fidelity Growth Fund",
      "annual_return_rate": 0.12,
      "volatility": 0.25,
      "portfolio_diversity_score": 0.6
    },
    "fraud_indicators": {
      "suspicious_flag": "True",
      "anomaly_score": 0.95,
      "transaction_amount": 25000,
      "transaction_date": "2024-01-20T14:15:00",
      "transaction_channel": "Online",
      "ip_address": "192.168.1.100",
      "device_id": "mobile_001",
      "geo_location": "New York, NY",
      "time_of_transaction": "2024-01-20T14:15:00",
      "transaction_pattern_score": 0.88,
      "previous_fraud_flag": "True",
      "account_age": 5
    }
  }
}
```

## SQL Queries Used

### Advisor Dashboard Query
```sql
SELECT 
    u.id as user_id,
    u.full_name,
    p.age, p.gender, p.country, p.employment_status,
    p.annual_income, p.current_savings, p.retirement_age_goal,
    p.risk_tolerance, p.contribution_amount, p.employer_contribution,
    p.total_annual_contribution, p.years_contributed,
    p.projected_pension_amount, p.expected_annual_payout,
    p.portfolio_diversity_score, p.volatility, p.suspicious_flag,
    p.anomaly_score, p.marital_status, p.number_of_dependents,
    p.education_level, p.health_status, p.debt_level,
    p.monthly_expenses, p.savings_rate, p.investment_experience_level,
    p.financial_goals, p.insurance_coverage, p.pension_type
FROM users u
INNER JOIN advisor_clients ac ON u.id = ac.resident_id
INNER JOIN pension_data p ON u.id = p.user_id
WHERE ac.advisor_id = :advisor_id
```

### Regulator Dashboard Query
```sql
SELECT 
    u.id as user_id, u.full_name, u.email,
    p.age, p.gender, p.country, p.annual_income, p.current_savings,
    p.risk_tolerance, p.suspicious_flag, p.anomaly_score,
    p.transaction_amount, p.transaction_date, p.geo_location,
    p.ip_address, p.device_id, p.time_of_transaction,
    p.transaction_pattern_score, p.previous_fraud_flag, p.account_age,
    p.portfolio_diversity_score, p.volatility, p.debt_level,
    p.monthly_expenses, p.savings_rate
FROM users u
INNER JOIN pension_data p ON u.id = p.user_id
ORDER BY p.anomaly_score DESC NULLS LAST
```

### User Details Query
```sql
SELECT 
    u.id as user_id, u.full_name, u.email, u.role,
    p.*
FROM users u
INNER JOIN pension_data p ON u.id = p.user_id
WHERE u.id = :user_id
```

## Frontend Integration

### Dashboard Components

#### Resident Dashboard
- Personal pension overview
- Risk profile visualization
- Fraud indicators
- Contribution tracking

#### Advisor Dashboard
- Client overview cards
- Risk tolerance distribution charts
- Age group analysis
- Income level breakdowns
- Fraud risk alerts

#### Regulator Dashboard
- Fraud risk heatmap
- Geographic risk distribution
- Transaction pattern analysis
- Suspicious activity alerts
- Compliance monitoring tools

### Data Visualization with Plotly

The API provides structured data perfect for creating:
- **Bar Charts**: Risk distributions, age groups, income levels
- **Pie Charts**: Portfolio allocations, risk tolerances
- **Heatmaps**: Geographic fraud risk patterns
- **Scatter Plots**: Risk vs. return analysis
- **Line Charts**: Transaction pattern trends

## Security Features

1. **Role-Based Access Control**: Each endpoint checks user role before allowing access
2. **Client Relationship Verification**: Advisors can only see their own clients
3. **JWT Authentication**: All endpoints require valid authentication tokens
4. **Data Isolation**: Users can only access data appropriate for their role

## Usage Examples

### Frontend API Calls

```javascript
// Resident Dashboard
const residentData = await fetch('/resident/dashboard', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Advisor Dashboard
const advisorData = await fetch('/advisor/dashboard', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Regulator Dashboard
const regulatorData = await fetch('/regulator/dashboard', {
  headers: { 'Authorization': `Bearer ${token}` }
});

// Client Details (Advisor)
const clientDetails = await fetch(`/advisor/client/${clientId}/details`, {
  headers: { 'Authorization': `Bearer ${token}` }
});

// User Details (Regulator)
const userDetails = await fetch(`/regulator/user/${userId}/details`, {
  headers: { 'Authorization': `Bearer ${token}` }
});
```

## Benefits

1. **Clear Separation**: Each role has dedicated endpoints with appropriate data access
2. **Efficient Queries**: Raw SQL queries for optimal performance
3. **Rich Data**: Comprehensive information for each role's needs
4. **Scalable**: Easy to extend with additional grouping options
5. **Secure**: Proper access control and data isolation
6. **Frontend Ready**: Structured data perfect for visualization libraries

This role-based architecture ensures that your pension AI system provides appropriate data access while maintaining security and performance.
