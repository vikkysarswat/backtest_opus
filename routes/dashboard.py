"""
Dashboard Routes
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@dashboard_bp.route('/home')
@login_required
def home():
    from app import Strategy, Backtest, DataFile
    
    stats = {
        'total_strategies': Strategy.query.filter_by(user_id=current_user.id).count(),
        'total_backtests': Backtest.query.filter_by(user_id=current_user.id).count(),
        'total_files': DataFile.query.filter_by(user_id=current_user.id).count(),
        'completed_backtests': Backtest.query.filter_by(user_id=current_user.id, status='completed').count()
    }
    
    recent_backtests = Backtest.query.filter_by(user_id=current_user.id).order_by(Backtest.created_at.desc()).limit(5).all()
    recent_strategies = Strategy.query.filter_by(user_id=current_user.id).order_by(Strategy.created_at.desc()).limit(5).all()
    data_files = DataFile.query.filter_by(user_id=current_user.id).order_by(DataFile.uploaded_at.desc()).limit(5).all()
    performance = calculate_overall_performance(current_user.id)
    
    return render_template('dashboard.html', stats=stats, recent_backtests=recent_backtests,
                          recent_strategies=recent_strategies, data_files=data_files, performance=performance)


def calculate_overall_performance(user_id):
    from app import Backtest
    import json
    
    completed_backtests = Backtest.query.filter_by(user_id=user_id, status='completed').all()
    
    if not completed_backtests:
        return {'total_pnl': 0, 'avg_win_rate': 0, 'best_strategy': None, 'total_trades': 0}
    
    total_pnl = 0
    total_trades = 0
    win_rates = []
    best_pnl = float('-inf')
    best_strategy = None
    
    for bt in completed_backtests:
        if bt.results:
            results = bt.results if isinstance(bt.results, dict) else json.loads(bt.results)
            pnl = results.get('total_pnl', 0)
            total_pnl += pnl
            total_trades += results.get('total_trades', 0)
            win_rates.append(results.get('win_rate', 0))
            if pnl > best_pnl:
                best_pnl = pnl
                best_strategy = bt.strategy.name if bt.strategy else bt.name
    
    return {
        'total_pnl': round(total_pnl, 2),
        'avg_win_rate': round(sum(win_rates) / len(win_rates), 2) if win_rates else 0,
        'best_strategy': best_strategy,
        'total_trades': total_trades
    }


@dashboard_bp.route('/stats')
@login_required
def get_stats():
    from app import Strategy, Backtest, DataFile
    
    stats = {
        'strategies': Strategy.query.filter_by(user_id=current_user.id).count(),
        'backtests': Backtest.query.filter_by(user_id=current_user.id).count(),
        'files': DataFile.query.filter_by(user_id=current_user.id).count(),
        'performance': calculate_overall_performance(current_user.id)
    }
    return jsonify(stats)
