from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.user import User
from app.models.gamification import Badge, UserBadge
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GamificationService:
    
    def award_points(self, db: Session, user_id: str, points: int, reason: str = None):
        """
        Add points to a user and check for new badges.
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
            
        user.points += points
        # Update reputation logic if needed (e.g. verified report adds reputation)
        if points > 0:
             # Cap reputation at 1000? Or just let it grow.
             user.reputation_score = min(1000, user.reputation_score + (points // 10))
        
        db.commit()
        db.refresh(user)
        
        self.check_badges(db, user_id)
        return user.points

    def check_badges(self, db: Session, user_id: str):
        """
        Check and award any new badges based on updated stats.
        Supports: points_threshold, reports_count, people_helped, streak_days
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        # 1. Get all badges
        all_badges = db.query(Badge).all()
        
        # 2. Get user's current badges
        user_badges = db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
        owned_badge_ids = {ub.badge_id for ub in user_badges}
        
        new_badges = []
        for badge in all_badges:
            if badge.id in owned_badge_ids:
                continue
                
            # Check requirements based on type
            awarded = False
            
            if badge.requirement_type == 'points_threshold':
                if user.points >= badge.requirement_value:
                    awarded = True
                    
            elif badge.requirement_type == 'reports_count':
                if (user.total_reports or 0) >= badge.requirement_value:
                    awarded = True
                    
            elif badge.requirement_type == 'people_helped':
                if (user.total_people_helped or 0) >= badge.requirement_value:
                    awarded = True
                    
            elif badge.requirement_type == 'streak_days':
                if (user.longest_streak or 0) >= badge.requirement_value:
                    awarded = True
            
            if awarded:
                new_ub = UserBadge(user_id=user_id, badge_id=badge.id)
                db.add(new_ub)
                new_badges.append(badge.name)
        
        if new_badges:
            db.commit()
            logger.info(f"User {user.full_name} earned badges: {new_badges}")

    def get_leaderboard(self, db: Session, limit: int = 10):
        """
        Return top users by points.
        """
        return db.query(User).order_by(desc(User.points)).limit(limit).all()

    def seed_badges(self, db: Session):
        """
        Create default badges based on Cameroon's North West Grassfields nobility system.
        """
        defaults = [
            # Contribution Tier Badges (The Nobility Ladder)
            {"name": "Nkwetoh", "desc": "First report - 'Young one', beginning the journey", "type": "reports_count", "val": 1, "icon": "🌱"},
            {"name": "Sheey", "desc": "25 reports - Entry-level noble, community helper", "type": "reports_count", "val": 25, "icon": "🪶"},
            {"name": "Faay", "desc": "100 reports - Trusted advisor, earned through service", "type": "reports_count", "val": 100, "icon": "🪶🪶"},
            {"name": "Shuufaay", "desc": "300 reports - Senior noble, voice in councils", "type": "reports_count", "val": 300, "icon": "🪶🪶🪶"},
            {"name": "Kwifor", "desc": "700 reports - Council of elders, kingmakers", "type": "reports_count", "val": 700, "icon": "👑"},
            {"name": "Fon", "desc": "1500 reports - The paramount chief, highest honor", "type": "reports_count", "val": 1500, "icon": "🦁👑"},
            
            # Points Threshold Badges (Legacy support)
            {"name": "Scout", "desc": "Earn 50 points", "type": "points_threshold", "val": 50, "icon": "🧭"},
            {"name": "Guardian", "desc": "Earn 200 points", "type": "points_threshold", "val": 200, "icon": "🛡️"},
            {"name": "Legend", "desc": "Earn 1000 points", "type": "points_threshold", "val": 1000, "icon": "👑"},
            
            # Impact Badges (The Protectors)
            {"name": "Nchinda", "desc": "Help 50 people avoid incidents - Palace messenger", "type": "people_helped", "val": 50, "icon": "🛡️"},
            {"name": "Ngwerong", "desc": "Help 250 people - Secret society protector", "type": "people_helped", "val": 250, "icon": "⚔️"},
            {"name": "Takumbeng", "desc": "Help 1000 people - Sacred guardian society", "type": "people_helped", "val": 1000, "icon": "🔥"},
            
            # Streak Badges
            {"name": "Mfor-ngong", "desc": "30-day streak - Steady heart", "type": "streak_days", "val": 30, "icon": "🔗"},
            {"name": "Eternal Flame", "desc": "100-day streak", "type": "streak_days", "val": 100, "icon": "🔥"},
        ]
        
        for b in defaults:
            exists = db.query(Badge).filter(Badge.name == b['name']).first()
            if not exists:
                new_badge = Badge(
                    name=b['name'],
                    description=b['desc'],
                    requirement_type=b['type'],
                    requirement_value=b['val'],
                    icon_url=b['icon']
                )
                db.add(new_badge)
        db.commit()

gamification_service = GamificationService()
