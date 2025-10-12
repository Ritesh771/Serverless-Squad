# Admin Dashboard API Documentation

This document describes the three new admin features implemented for the HomeServe Pro backend:

## 1. Cache Management Interface 🗄️

### Overview
Provides admin control over clearing and monitoring cached data (search results, sessions, API data, etc.)

### Endpoints

#### GET `/admin-dashboard/cache/`
Get comprehensive cache statistics and health information.

**Authentication Required:** Super Admin or Ops Manager

**Response:**
```json
{
  "status": "success",
  "cache_stats": {
    "default": {
      "name": "default", 
      "backend": "RedisCache",
      "timeout": 900,
      "key_prefix": "homeserve_cache",
      "redis_version": "7.0.0",
      "used_memory": "2.5M",
      "connected_clients": 3,
      "keyspace_hits": 1250,
      "keyspace_misses": 45,
      "hit_rate_percentage": 96.5,
      "total_keys": 123
    },
    "sessions": { /* similar structure */ },
    "search_results": { /* similar structure */ },
    "api_data": { /* similar structure */ },
    "overall_health": {
      "healthy_caches": 4,
      "total_caches": 4,
      "health_percentage": 100.0,
      "average_hit_rate": 94.2,
      "status": "healthy"
    }
  },
  "timestamp": "2025-10-12T08:30:00Z"
}
```

#### POST `/admin-dashboard/cache/`
Clear specific cache categories.

**Authentication Required:** Super Admin or Ops Manager

**Request Body:**
```json
{
  "cache_type": "all"  // Options: "all", "default", "sessions", "search_results", "api_data"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Cache \"all\" cleared successfully",
  "result": {
    "cleared": ["default", "sessions", "search_results", "api_data"],
    "errors": []
  }
}
```

### Cache Categories
- **default**: General application cache
- **sessions**: User session data
- **search_results**: Search query results (30min TTL)  
- **api_data**: API response cache (10min TTL)

---

## 2. Pincode Scaling Map Visualization 🗺️

### Overview
Visualizes demand, service density, and vendor availability on a live map by pincode.

### Endpoints

#### GET `/admin-dashboard/pincode-scaling/`
Get aggregated booking and vendor data by pincode for map visualization.

**Authentication Required:** Admin User (Super Admin, Ops Manager, Onboard Manager)

**Query Parameters:**
- `service_type` (optional): Filter by service category
- `days_back` (optional): Number of days to look back (default: 30)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "pincode": "110001",
      "total_bookings": 45,
      "completed_bookings": 38,
      "pending_bookings": 5,
      "cancelled_bookings": 2,
      "completion_rate": 84.44,
      "cancellation_rate": 4.44,
      "available_vendors": 8,
      "demand_intensity": 5.63,
      "estimated_wait_time_hours": 0.6,
      "zone_status": "optimal",
      "heat_intensity": 56
    }
  ],
  "summary": {
    "total_pincodes": 25,
    "total_bookings": 1250,
    "total_vendors": 150,
    "high_demand_zones": 3,
    "optimal_zones": 18,
    "date_range": {
      "start": "2025-09-12T08:30:00Z",
      "end": "2025-10-12T08:30:00Z", 
      "days": 30
    },
    "service_categories": ["plumbing", "electrical", "cleaning", "maintenance"]
  },
  "timestamp": "2025-10-12T08:30:00Z"
}
```

### Zone Status Types
- **high_demand_low_supply**: Demand intensity > 10, vendors < 3
- **low_demand_high_supply**: Demand intensity < 2, vendors > 5  
- **optimal**: Completion rate > 80%, cancellation rate < 10%
- **balanced**: Everything else

### Heat Map Values
- `heat_intensity`: 0-100 scale for map color intensity
- `demand_intensity`: Bookings per vendor ratio
- `estimated_wait_time_hours`: Simplified wait time calculation

---

## 3. Global Edit History Diff Viewer 🧾

### Overview  
Allows admins to see side-by-side visual differences of changes made anywhere in the system with complete audit trails.

### Endpoints

#### GET `/admin-dashboard/edit-history/`
Get audit log data with diff visualization capabilities.

**Authentication Required:** Super Admin only

**Query Parameters:**
- `model` (optional): Filter by model name
- `user` (optional): Filter by username
- `action` (optional): Filter by action type
- `start_date` (optional): ISO format start date
- `end_date` (optional): ISO format end date
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Results per page (default: 20)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 123,
      "user": "admin_user",
      "user_role": "super_admin",
      "action": "update", 
      "resource_type": "Booking",
      "resource_id": "uuid-here",
      "timestamp": "2025-10-12T08:30:00Z",
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "old_values": {
        "status": "pending",
        "total_price": "100.00"
      },
      "new_values": {
        "status": "confirmed", 
        "total_price": "120.00"
      },
      "diff": [
        {
          "field": "status",
          "old_value": "pending",
          "new_value": "confirmed",
          "change_type": "modified",
          "diff_lines": [
            "- pending",
            "+ confirmed"
          ]
        },
        {
          "field": "total_price", 
          "old_value": "100.00",
          "new_value": "120.00",
          "change_type": "modified",
          "diff_lines": [
            "- 100.00",
            "+ 120.00"
          ]
        }
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 500,
    "total_pages": 25,
    "has_next": true,
    "has_previous": false
  },
  "filter_options": {
    "models": ["Booking", "User", "Payment", "Signature"],
    "actions": ["create", "update", "delete", "login", "logout"],
    "users": ["admin_user", "ops_manager1", "vendor1"]
  },
  "timestamp": "2025-10-12T08:30:00Z"
}
```

#### POST `/admin-dashboard/edit-history/export/`
Export edit history as CSV or PDF for compliance.

**Authentication Required:** Super Admin only

**Request Body:**
```json
{
  "format": "csv",  // Options: "csv", "pdf"
  "filters": {
    "model": "Booking",
    "user": "admin_user", 
    "action": "update",
    "start_date": "2025-10-01T00:00:00Z",
    "end_date": "2025-10-12T23:59:59Z"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Export completed in CSV format",
  "record_count": 150,
  "download_data": "base64-encoded-file-content",
  "timestamp": "2025-10-12T08:30:00Z"
}
```

### Change Types
- **added**: Field was added (old value was null/not set)
- **removed**: Field was removed (new value is null/not set)  
- **modified**: Field value was changed

---

## 4. Combined Dashboard Stats 📊

### Overview
Provides a combined overview of all admin dashboard metrics.

### Endpoints  

#### GET `/admin-dashboard/dashboard/stats/`
Get combined dashboard statistics for admin overview.

**Authentication Required:** Admin User (Super Admin, Ops Manager, Onboard Manager)

**Response:**
```json
{
  "status": "success",
  "cache_health": {
    "healthy_caches": 4,
    "total_caches": 4, 
    "health_percentage": 100.0,
    "average_hit_rate": 94.2,
    "status": "healthy"
  },
  "activity_stats": {
    "total_actions_24h": 245,
    "unique_users_24h": 12,
    "top_actions": [
      {"action": "update", "count": 89},
      {"action": "create", "count": 67},
      {"action": "login", "count": 45}
    ]
  },
  "pincode_stats": {
    "total_pincodes_served": 25,
    "avg_bookings_per_pincode": 8.5,
    "active_vendors": 150
  },
  "timestamp": "2025-10-12T08:30:00Z"
}
```

---

## Authentication & Permissions

### Role Requirements
- **Cache Management**: Super Admin, Ops Manager
- **Pincode Scaling**: Super Admin, Ops Manager, Onboard Manager  
- **Edit History**: Super Admin only
- **Dashboard Stats**: Super Admin, Ops Manager, Onboard Manager

### Authentication Method
- JWT token in Authorization header: `Bearer <token>`
- Session authentication also supported

### Error Responses
```json
{
  "detail": "Authentication credentials were not provided."  // 401
}
```

```json
{
  "detail": "You do not have permission to perform this action."  // 403
}
```

---

## Implementation Features

### Security
✅ Role-based access control  
✅ Complete audit logging  
✅ IP address tracking  
✅ User agent logging  
✅ Tamper-proof edit trails

### Performance  
✅ Redis caching with multiple databases  
✅ Efficient database queries with aggregation  
✅ Pagination for large datasets  
✅ Optimized cache hit rates

### Monitoring
✅ Real-time cache statistics  
✅ Live demand heat maps  
✅ Complete change history  
✅ Export capabilities for compliance

### Error Handling
✅ Graceful Redis connection failures  
✅ Invalid filter parameter handling  
✅ Export size limitations  
✅ Timeout protection

---

## Cache Configuration

The system uses Redis with separate databases:
- **DB 0**: Channels/WebSocket data
- **DB 1**: Default cache (15min TTL)  
- **DB 2**: Sessions (24hr TTL)
- **DB 3**: Search results (30min TTL)
- **DB 4**: API data (10min TTL)

---

## Next Steps for Frontend Integration

1. **Map Component**: Use data from pincode scaling API with Leaflet.js or Google Maps
2. **Cache Dashboard**: Real-time charts showing cache health and hit rates  
3. **Diff Viewer**: Side-by-side comparison component for edit history
4. **Export Handler**: Download functionality for audit reports
5. **Real-time Updates**: WebSocket integration for live statistics