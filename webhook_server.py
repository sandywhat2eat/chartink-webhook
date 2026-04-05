#!/usr/bin/env python3
"""
ChartInk Webhook Server
Receives webhook alerts from ChartInk and stores them in Supabase
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from flask import Flask, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
import requests as http_requests

# Load environment variables
load_dotenv()

# Configure logging - use environment-appropriate log file path
import tempfile
log_file = os.getenv('LOG_FILE', os.path.join(tempfile.gettempdir(), 'webhook.log'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only use console logging for Digital Ocean
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Missing Supabase configuration in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

class ChartInkWebhookProcessor:
    """Process ChartInk webhook payloads and store in database"""
    
    @staticmethod
    def parse_stocks_string(stocks_string: str) -> Tuple[List[str], List[float]]:
        """
        Parse stocks string from ChartInk webhook
        
        Args:
            stocks_string: "SEPOWER@3.75,ASTEC@541.8,EDUCOMP@2.1" (old format)
            OR just "SEPOWER,ASTEC,EDUCOMP" (new ChartInk format)
            
        Returns:
            Tuple of (stock_symbols, trigger_prices)
        """
        if not stocks_string or not stocks_string.strip():
            return [], []
            
        try:
            # Check if it's the old format with @ symbols
            if '@' in stocks_string:
                stocks_data = stocks_string.split(',')
                stocks = []
                prices = []
                
                for item in stocks_data:
                    item = item.strip()
                    if '@' not in item:
                        logger.warning(f"Invalid stock format: {item}")
                        continue
                        
                    parts = item.split('@')
                    if len(parts) != 2:
                        logger.warning(f"Invalid stock format: {item}")
                        continue
                        
                    symbol = parts[0].strip()
                    try:
                        price = float(parts[1].strip())
                        stocks.append(symbol)
                        prices.append(price)
                    except ValueError:
                        logger.warning(f"Invalid price format: {parts[1]}")
                        continue
                        
                return stocks, prices
            else:
                # New ChartInk format: just comma-separated stock symbols
                stocks = [stock.strip() for stock in stocks_string.split(',') if stock.strip()]
                return stocks, []  # Prices will be handled separately
                
        except Exception as e:
            logger.error(f"Error parsing stocks string: {e}")
            return [], []
    
    @staticmethod
    def calculate_price_metrics(prices: List[float]) -> Dict[str, Optional[float]]:
        """Calculate price statistics"""
        if not prices:
            return {
                'avg_trigger_price': None,
                'min_trigger_price': None,
                'max_trigger_price': None
            }
            
        return {
            'avg_trigger_price': round(sum(prices) / len(prices), 2),
            'min_trigger_price': min(prices),
            'max_trigger_price': max(prices)
        }
    
    @staticmethod
    def validate_webhook_payload(payload: Dict) -> Tuple[bool, str]:
        """Validate incoming webhook payload"""
        required_fields = ['scan_name', 'scan_url', 'alert_name', 'stocks']
        
        for field in required_fields:
            if field not in payload:
                return False, f"Missing required field: {field}"
                
        if not isinstance(payload.get('stocks'), str):
            return False, "stocks field must be a string"
            
        return True, "Valid payload"
    
    @classmethod
    def process_webhook(cls, payload: Dict) -> Dict:
        """
        Process ChartInk webhook payload and store in database
        
        Args:
            payload: ChartInk webhook payload
            
        Returns:
            Dict with processing results
        """
        try:
            # Validate payload
            is_valid, message = cls.validate_webhook_payload(payload)
            if not is_valid:
                return {'success': False, 'error': message}
            
            # Handle ChartInk's actual format with separate stocks and trigger_prices fields
            if 'trigger_prices' in payload and isinstance(payload['trigger_prices'], str):
                # New ChartInk format: separate stocks and trigger_prices strings
                stocks_str = payload['stocks']
                prices_str = payload['trigger_prices']
                
                # Parse stocks (comma-separated)
                stocks = [stock.strip() for stock in stocks_str.split(',') if stock.strip()]
                
                # Parse prices (comma-separated)
                try:
                    prices = [float(price.strip()) for price in prices_str.split(',') if price.strip()]
                except ValueError as e:
                    return {'success': False, 'error': f'Invalid price format: {e}'}
                
                if len(stocks) != len(prices):
                    return {'success': False, 'error': f'Mismatch: {len(stocks)} stocks vs {len(prices)} prices'}
                    
            else:
                # Old format: "SYMBOL@PRICE,SYMBOL@PRICE"
                stocks, prices = cls.parse_stocks_string(payload['stocks'])
                
                if not stocks:
                    return {'success': False, 'error': 'No valid stocks found in payload'}
                
                if len(stocks) != len(prices):
                    return {'success': False, 'error': 'Mismatch between stocks and prices count'}
            
            # Calculate metrics
            total_stocks = len(stocks)
            price_metrics = cls.calculate_price_metrics(prices)
            
            # Prepare data for database (matching existing schema)
            alert_data = {
                'scan_name': payload['scan_name'],
                'scan_url': payload['scan_url'],
                'alert_name': payload['alert_name'],
                'stocks': stocks,
                'trigger_prices': prices,
                'total_stocks': total_stocks,
                'avg_trigger_price': price_metrics['avg_trigger_price'],
                'min_trigger_price': price_metrics['min_trigger_price'],
                'max_trigger_price': price_metrics['max_trigger_price'],
                'processing_status': 'new',
                'source_platform': 'ChartInk'
            }
            
            # Insert into Supabase
            result = supabase.table('chartink_alerts').insert(alert_data).execute()
            
            if result.data:
                logger.info(f"Successfully stored alert: {payload['scan_name']} with {total_stocks} stocks")
                return {
                    'success': True,
                    'message': 'Alert stored successfully',
                    'data': {
                        'id': result.data[0]['id'],
                        'total_stocks': total_stocks,
                        'avg_price': price_metrics['avg_trigger_price']
                    }
                }
            else:
                logger.error(f"Failed to insert data: {result}")
                return {'success': False, 'error': 'Database insertion failed'}
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {'success': False, 'error': str(e)}

# Webhook endpoint
@app.route('/webhook/chartink', methods=['POST'])
def chartink_webhook():
    """ChartInk webhook endpoint"""
    try:
        # Get JSON payload
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        payload = request.get_json()
        if not payload:
            return jsonify({'error': 'Empty payload'}), 400
        
        logger.info(f"Received webhook: {json.dumps(payload, indent=2)}")
        
        # Process webhook
        result = ChartInkWebhookProcessor.process_webhook(payload)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Webhook endpoint error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        result = supabase.table('chartink_alerts').select('id').limit(1).execute()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

# Test endpoint for manual testing
@app.route('/test', methods=['POST'])
def test_webhook():
    """Test endpoint with sample data"""
    sample_payload = {
        "scan_name": "Short term breakouts",
        "scan_url": "short-term-breakouts",
        "alert_name": "Alert for Short term breakouts",
        "stocks": "SEPOWER@3.75,ASTEC@541.8,EDUCOMP@2.1,KSERASERA@0.2"
    }
    
    result = ChartInkWebhookProcessor.process_webhook(sample_payload)
    return jsonify(result)

# Get recent alerts endpoint
@app.route('/alerts/recent', methods=['GET'])
def get_recent_alerts():
    """Get recent alerts from database"""
    try:
        limit = request.args.get('limit', 10, type=int)
        limit = min(limit, 100)  # Cap at 100
        
        result = supabase.table('chartink_alerts')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        return jsonify({
            'success': True,
            'count': len(result.data),
            'alerts': result.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching recent alerts: {e}")
        return jsonify({'error': str(e)}), 500


# ============================================
# TradingView Webhook to Discord Relay
# ============================================
# Dynamically routes to Discord webhooks based on strategy in controls table
# Payload should contain "strategy" field (e.g., "INDEX_FUTURES_MANAGER", "trade_ai")

# Cache for webhook lookups (refreshed on miss)
_webhook_cache = {}
_cache_timestamp = None
CACHE_TTL_SECONDS = 300  # 5 minutes

def get_webhook_for_strategy(strategy: str) -> Optional[str]:
    """
    Look up discord_webhook_url from controls table by strategy.
    Supports multiple matching patterns:
    - Exact match: "INDEX_FUTURES_MANAGER"
    - Case-insensitive: "index_futures_manager"
    - Partial match for _ai suffix: "trade_ai" matches strategies containing "TRADE" or "LONG" or "SHORT"
    """
    global _webhook_cache, _cache_timestamp
    import time

    now = time.time()

    # Refresh cache if stale
    if _cache_timestamp is None or (now - _cache_timestamp) > CACHE_TTL_SECONDS:
        try:
            result = supabase.table('controls')\
                .select('strategy, discord_webhook_url')\
                .not_.is_('discord_webhook_url', 'null')\
                .execute()

            _webhook_cache = {row['strategy'].upper(): row['discord_webhook_url'] for row in result.data}
            _cache_timestamp = now
            logger.info(f"Webhook cache refreshed: {len(_webhook_cache)} strategies")
        except Exception as e:
            logger.error(f"Failed to refresh webhook cache: {e}")
            # Continue with stale cache if available

    strategy_upper = strategy.upper().replace("-", "_")

    # 1. Exact match
    if strategy_upper in _webhook_cache:
        return _webhook_cache[strategy_upper]

    # 2. Handle *_ai suffixes - map to specific strategies
    ai_mappings = {
        'TRADE_AI': ['LONG_AGENT', 'SHORT_AGENT', 'FUND_MANAGER'],
        'EQUITY_AI': ['EQUITY_FUND_MANAGER', 'CHIEF_PORTFOLIO_MANAGER'],
        'FUTURES_AI': ['FUTURES_MANAGER', 'FUTURES_FUND_MANAGER'],
        'OPTIONS_AI': ['OPTIONS_MANAGER'],
        'INDICES_AI': ['INDEX_FUTURES_MANAGER'],
        'COMMODITIES_AI': ['COMMODITIES_MANAGER'],
        'SOROS_AI': ['SOROS_MANAGING_PARTNER'],
        'CIO_AI': ['CIO'],
    }

    if strategy_upper in ai_mappings:
        for mapped_strategy in ai_mappings[strategy_upper]:
            if mapped_strategy in _webhook_cache:
                return _webhook_cache[mapped_strategy]

    # 3. Partial match (find first strategy containing the search term)
    for cached_strategy, webhook_url in _webhook_cache.items():
        if strategy_upper in cached_strategy or cached_strategy in strategy_upper:
            return webhook_url

    return None

def get_available_strategies() -> List[str]:
    """Return list of strategies that have webhooks configured"""
    global _webhook_cache
    if not _webhook_cache:
        get_webhook_for_strategy("_refresh_cache_")  # Force cache load
    return sorted(_webhook_cache.keys())

@app.route("/webhook/tradingview", methods=["POST"])
def tradingview_webhook():
    try:
        body = request.get_data(as_text=True).strip()
        logger.info(f"TradingView webhook received: {body[:300]}")
        if not body:
            return jsonify({"error": "Empty body"}), 400
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            # Plain text — send to default (CIO channel)
            payload = {"content": body, "strategy": "CIO"}

        # Route by "strategy" or "agent" field in payload
        strategy = payload.get("strategy") or payload.get("agent") or "CIO"
        webhook_url = get_webhook_for_strategy(strategy)

        if not webhook_url:
            available = get_available_strategies()
            logger.warning(f"No webhook for strategy '{strategy}'. Available: {available[:20]}...")
            return jsonify({
                "error": f"No webhook configured for strategy '{strategy}'",
                "available_strategies": available[:30],
                "hint": "Use strategy names from controls table or shortcuts like 'trade_ai', 'equity_ai'"
            }), 400

        # Build Discord message from "content" field
        content = payload.get("content", json.dumps(payload, indent=2))
        discord_payload = {"content": content}
        if payload.get("username"):
            discord_payload["username"] = payload["username"]

        resp = http_requests.post(webhook_url, json=discord_payload, timeout=5)
        logger.info(f"Discord response for strategy '{strategy}': {resp.status_code}")
        return jsonify({"success": True, "strategy": strategy, "discord_status": resp.status_code}), 200
    except Exception as e:
        logger.error(f"TradingView webhook error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/webhook/tradingview/test", methods=["GET"])
def tradingview_test():
    """Test endpoint showing available strategies"""
    available = get_available_strategies()
    return jsonify({
        "status": "ready",
        "strategies_with_webhooks": len(available),
        "sample_strategies": available[:20],
        "shortcuts": ["trade_ai", "equity_ai", "futures_ai", "options_ai", "indices_ai", "commodities_ai", "soros_ai", "cio_ai"]
    }), 200

if __name__ == '__main__':
    logger.info("Starting ChartInk Webhook Server...")
    logger.info(f"Supabase URL: {SUPABASE_URL}")
    
    # Get port from environment variable for Digital Ocean App Platform
    port = int(os.getenv('PORT', 8082))
    
    # Run the server
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
