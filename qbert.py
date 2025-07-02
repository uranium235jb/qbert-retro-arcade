import pygame
import sys
import math
import numpy as np

# Initialize Pygame
pygame.init()

# Initialize audio with error handling
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    AUDIO_AVAILABLE = True
    print("Audio initialized successfully")
except pygame.error as e:
    print(f"Audio not available: {e}")
    AUDIO_AVAILABLE = False

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors - Sharp Neon Palette
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Ultra-Sharp Neon Colors
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 0, 255)
NEON_GREEN = (0, 255, 0)
NEON_PURPLE = (128, 0, 255)
NEON_ORANGE = (255, 128, 0)
NEON_BLUE = (0, 128, 255)
ELECTRIC_BLUE = (0, 191, 255)
HOT_PINK = (255, 20, 147)
LASER_RED = (255, 0, 64)
ACID_GREEN = (128, 255, 0)

# Level-based color schemes
COLOR_SCHEMES = {
    1: {  # Level 1 - Cyan Theme
        'original_top': (40, 40, 60),
        'original_left': (25, 25, 45),
        'original_right': (15, 15, 35),
        'original_edge': (60, 60, 80),
        'target_top': (0, 255, 255),      # Cyan
        'target_left': (0, 200, 255),
        'target_right': (0, 150, 255),
        'target_edge': (128, 255, 255),
        'explosion_colors': [(255, 255, 255), (0, 255, 255), (255, 0, 255), (0, 255, 0), (255, 255, 0)]
    },
    2: {  # Level 2 - Hot Pink Theme
        'original_top': (60, 20, 40),
        'original_left': (45, 15, 30),
        'original_right': (35, 10, 25),
        'original_edge': (80, 30, 50),
        'target_top': (255, 20, 147),     # Hot Pink
        'target_left': (255, 50, 170),
        'target_right': (200, 15, 120),
        'target_edge': (255, 100, 200),
        'explosion_colors': [(255, 255, 255), (255, 20, 147), (255, 0, 255), (255, 100, 200), (255, 255, 0)]
    },
    3: {  # Level 3 - Acid Green Theme
        'original_top': (20, 60, 20),
        'original_left': (15, 45, 15),
        'original_right': (10, 35, 10),
        'original_edge': (30, 80, 30),
        'target_top': (128, 255, 0),      # Acid Green
        'target_left': (100, 255, 50),
        'target_right': (80, 200, 0),
        'target_edge': (180, 255, 100),
        'explosion_colors': [(255, 255, 255), (128, 255, 0), (0, 255, 0), (255, 255, 0), (0, 255, 255)]
    },
    4: {  # Level 4 - Electric Purple Theme
        'original_top': (60, 20, 80),
        'original_left': (45, 15, 60),
        'original_right': (35, 10, 50),
        'original_edge': (80, 30, 100),
        'target_top': (128, 0, 255),      # Electric Purple
        'target_left': (150, 50, 255),
        'target_right': (100, 0, 200),
        'target_edge': (180, 100, 255),
        'explosion_colors': [(255, 255, 255), (128, 0, 255), (255, 0, 255), (191, 64, 191), (0, 255, 255)]
    },
    5: {  # Level 5 - Laser Red Theme
        'original_top': (80, 20, 20),
        'original_left': (60, 15, 15),
        'original_right': (50, 10, 10),
        'original_edge': (100, 30, 30),
        'target_top': (255, 0, 64),       # Laser Red
        'target_left': (255, 50, 100),
        'target_right': (200, 0, 50),
        'target_edge': (255, 100, 150),
        'explosion_colors': [(255, 255, 255), (255, 0, 64), (255, 0, 0), (255, 100, 100), (255, 255, 0)]
    },
    6: {  # Level 6 - Electric Blue Theme
        'original_top': (20, 40, 80),
        'original_left': (15, 30, 60),
        'original_right': (10, 25, 50),
        'original_edge': (30, 50, 100),
        'target_top': (0, 191, 255),      # Electric Blue
        'target_left': (50, 200, 255),
        'target_right': (0, 150, 200),
        'target_edge': (100, 220, 255),
        'explosion_colors': [(255, 255, 255), (0, 191, 255), (0, 128, 255), (0, 255, 255), (128, 255, 255)]
    }
}

def get_color_scheme(level, progression_system=None):
    """Get color scheme for the current level, cycling through available schemes"""
    # Check if we have bonus themes unlocked
    if progression_system:
        available_themes = progression_system.get_available_themes()
        bonus_themes = progression_system.bonus_themes
        
        # Use bonus themes if available
        theme_count = len(available_themes)
        if theme_count > 6:
            # Include bonus themes in rotation
            theme_index = (level - 1) % theme_count
            theme_id = available_themes[theme_index]
            
            if theme_id in bonus_themes:
                return bonus_themes[theme_id]
    
    # Default theme rotation
    scheme_count = len(COLOR_SCHEMES)
    scheme_level = ((level - 1) % scheme_count) + 1
    return COLOR_SCHEMES[scheme_level]

class PowerUp:
    def __init__(self, row, col, x, y, power_type, sound_generator):
        self.row = row
        self.col = col
        self.x = x
        self.y = y
        self.power_type = power_type
        self.sound_generator = sound_generator
        self.size = 15
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 8000  # 8 seconds before disappearing
        self.pulse_timer = 0
        self.collected = False
        
        # Power-up specific properties
        self.power_configs = {
            'freeze': {
                'color': (0, 255, 255),      # Cyan
                'glow_color': (128, 255, 255),
                'duration': 3000,             # 3 seconds
                'name': 'FREEZE'
            },
            'speed': {
                'color': (255, 255, 0),      # Yellow
                'glow_color': (255, 255, 128),
                'duration': 5000,             # 5 seconds
                'name': 'SPEED'
            },
            'shield': {
                'color': (0, 255, 0),        # Green
                'glow_color': (128, 255, 128),
                'duration': 10000,            # 10 seconds
                'name': 'SHIELD'
            },
            'disc': {
                'color': (255, 0, 255),      # Magenta
                'glow_color': (255, 128, 255),
                'duration': 0,                # Instant use
                'name': 'FLYING DISC'
            },
            'bomb': {
                'color': (255, 128, 0),      # Orange
                'glow_color': (255, 200, 128),
                'duration': 0,                # Instant use
                'name': 'COLOR BOMB'
            }
        }
        
        self.config = self.power_configs[power_type]
    
    def update(self):
        """Update power-up animation and check if expired"""
        current_time = pygame.time.get_ticks()
        
        # Check if expired
        if current_time - self.spawn_time > self.lifetime:
            return False  # Should be removed
        
        # Update pulse animation
        self.pulse_timer = current_time
        return True
    
    def draw(self, screen):
        """Draw the power-up with pulsing glow effect"""
        if self.collected:
            return
            
        # Pulsing effect
        pulse = abs(math.sin(self.pulse_timer * 0.01)) * 0.5 + 0.5
        current_size = int(self.size * (0.8 + pulse * 0.4))
        
        # Draw glow effect
        glow_size = current_size + 8
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        glow_alpha = int(100 * pulse)
        pygame.draw.circle(glow_surf, (*self.config['glow_color'], glow_alpha), 
                          (glow_size, glow_size), glow_size)
        screen.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)))
        
        # Draw main power-up
        pygame.draw.circle(screen, self.config['color'], (int(self.x), int(self.y)), current_size)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), current_size, 2)
        
        # Draw power-up symbol
        self.draw_symbol(screen, current_size)
    
    def draw_symbol(self, screen, size):
        """Draw the power-up type symbol"""
        if self.power_type == 'freeze':
            # Draw snowflake-like symbol
            points = []
            for i in range(6):
                angle = i * math.pi / 3
                x = self.x + math.cos(angle) * (size - 5)
                y = self.y + math.sin(angle) * (size - 5)
                points.append((int(x), int(y)))
            for point in points:
                pygame.draw.line(screen, WHITE, (int(self.x), int(self.y)), point, 2)
                
        elif self.power_type == 'speed':
            # Draw lightning bolt
            bolt_points = [
                (int(self.x - 5), int(self.y - 8)),
                (int(self.x + 2), int(self.y - 2)),
                (int(self.x - 2), int(self.y + 2)),
                (int(self.x + 5), int(self.y + 8))
            ]
            for i in range(len(bolt_points) - 1):
                pygame.draw.line(screen, WHITE, bolt_points[i], bolt_points[i + 1], 3)
                
        elif self.power_type == 'shield':
            # Draw shield shape
            shield_points = [
                (int(self.x), int(self.y - 8)),
                (int(self.x + 6), int(self.y - 4)),
                (int(self.x + 6), int(self.y + 4)),
                (int(self.x), int(self.y + 8)),
                (int(self.x - 6), int(self.y + 4)),
                (int(self.x - 6), int(self.y - 4))
            ]
            pygame.draw.polygon(screen, WHITE, shield_points, 2)
            
        elif self.power_type == 'disc':
            # Draw flying disc
            pygame.draw.ellipse(screen, WHITE, 
                              (int(self.x - 8), int(self.y - 3), 16, 6), 2)
            pygame.draw.ellipse(screen, WHITE, 
                              (int(self.x - 5), int(self.y - 2), 10, 4), 1)
                              
        elif self.power_type == 'bomb':
            # Draw explosion symbol
            for i in range(8):
                angle = i * math.pi / 4
                x1 = self.x + math.cos(angle) * 4
                y1 = self.y + math.sin(angle) * 4
                x2 = self.x + math.cos(angle) * 8
                y2 = self.y + math.sin(angle) * 8
                pygame.draw.line(screen, WHITE, (int(x1), int(y1)), (int(x2), int(y2)), 2)

class Particle:
    def __init__(self, x, y, color, velocity, lifetime, size=2):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity  # (vx, vy)
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.gravity = 0.1
        
    def update(self):
        """Update particle position and lifetime"""
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.velocity = (self.velocity[0] * 0.98, self.velocity[1] + self.gravity)  # Air resistance + gravity
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, screen):
        """Draw the particle with fading alpha"""
        if self.lifetime <= 0:
            return
        
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        current_size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
        
        # Create surface with alpha
        particle_surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(particle_surf, (*self.color, alpha), (current_size, current_size), current_size)
        screen.blit(particle_surf, (int(self.x - current_size), int(self.y - current_size)))

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_explosion(self, x, y, color, count=15):
        """Add explosion particles"""
        import random
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            lifetime = random.randint(20, 40)
            size = random.randint(2, 4)
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime, size))
    
    def add_trail(self, x, y, color, count=5):
        """Add trail particles"""
        import random
        for _ in range(count):
            vx = random.uniform(-1, 1)
            vy = random.uniform(-1, 1)
            lifetime = random.randint(10, 20)
            size = random.randint(1, 3)
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime, size))
    
    def add_sparks(self, x, y, color, count=8):
        """Add spark particles"""
        import random
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed - 2  # Upward bias
            lifetime = random.randint(15, 30)
            size = random.randint(1, 2)
            self.particles.append(Particle(x, y, color, (vx, vy), lifetime, size))
    
    def update(self):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, screen):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)

class ScreenShake:
    def __init__(self):
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_offset = (0, 0)
    
    def add_shake(self, duration, intensity):
        """Add screen shake effect"""
        self.shake_duration = max(self.shake_duration, duration)
        self.shake_intensity = max(self.shake_intensity, intensity)
    
    def update(self):
        """Update screen shake"""
        if self.shake_duration > 0:
            import random
            intensity = int(self.shake_intensity)  # Convert to int for randint
            shake_x = random.randint(-intensity, intensity) if intensity > 0 else 0
            shake_y = random.randint(-intensity, intensity) if intensity > 0 else 0
            self.shake_offset = (shake_x, shake_y)
            self.shake_duration -= 1
            self.shake_intensity = max(0, self.shake_intensity - 0.2)
        else:
            self.shake_offset = (0, 0)
    
    def get_offset(self):
        """Get current shake offset"""
        return self.shake_offset

class AnimatedBackground:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.stars = []
        self.geometric_shapes = []
        self.time = 0
        
        # Create starfield
        import random
        for _ in range(100):
            x = random.randint(0, width)
            y = random.randint(0, height)
            speed = random.uniform(0.1, 0.5)
            brightness = random.randint(50, 200)
            size = random.randint(1, 3)
            self.stars.append({
                'x': x, 'y': y, 'speed': speed, 
                'brightness': brightness, 'size': size,
                'twinkle_phase': random.uniform(0, 2 * math.pi)
            })
        
        # Create geometric shapes
        for _ in range(8):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(20, 60)
            rotation_speed = random.uniform(-0.02, 0.02)
            shape_type = random.choice(['triangle', 'diamond', 'hexagon'])
            color = random.choice([
                (0, 100, 150, 30),   # Dark blue
                (100, 0, 150, 30),   # Dark purple
                (0, 150, 100, 30),   # Dark teal
                (150, 0, 100, 30)    # Dark magenta
            ])
            self.geometric_shapes.append({
                'x': x, 'y': y, 'size': size, 'rotation': 0,
                'rotation_speed': rotation_speed, 'type': shape_type,
                'color': color, 'pulse_phase': random.uniform(0, 2 * math.pi)
            })
    
    def update(self):
        """Update animated background elements"""
        self.time += 1
        
        # Update stars
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > self.height:
                star['y'] = -5
                import random
                star['x'] = random.randint(0, self.width)
            
            # Update twinkle
            star['twinkle_phase'] += 0.1
        
        # Update geometric shapes
        for shape in self.geometric_shapes:
            shape['rotation'] += shape['rotation_speed']
            shape['pulse_phase'] += 0.05
    
    def draw(self, screen):
        """Draw animated background"""
        # Draw stars
        for star in self.stars:
            twinkle = abs(math.sin(star['twinkle_phase']))
            brightness = int(star['brightness'] * (0.5 + 0.5 * twinkle))
            color = (brightness, brightness, brightness)
            
            if star['size'] == 1:
                screen.set_at((int(star['x']), int(star['y'])), color)
            else:
                pygame.draw.circle(screen, color, (int(star['x']), int(star['y'])), star['size'])
        
        # Draw geometric shapes
        for shape in self.geometric_shapes:
            pulse = abs(math.sin(shape['pulse_phase']))
            current_size = int(shape['size'] * (0.8 + 0.2 * pulse))
            alpha = int(shape['color'][3] * (0.5 + 0.5 * pulse))
            
            # Create surface for shape with alpha
            shape_surf = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
            color_with_alpha = (*shape['color'][:3], alpha)
            
            if shape['type'] == 'triangle':
                points = []
                for i in range(3):
                    angle = shape['rotation'] + i * 2 * math.pi / 3
                    x = current_size + math.cos(angle) * current_size * 0.8
                    y = current_size + math.sin(angle) * current_size * 0.8
                    points.append((x, y))
                pygame.draw.polygon(shape_surf, color_with_alpha, points, 2)
                
            elif shape['type'] == 'diamond':
                points = []
                for i in range(4):
                    angle = shape['rotation'] + i * math.pi / 2
                    x = current_size + math.cos(angle) * current_size * 0.8
                    y = current_size + math.sin(angle) * current_size * 0.8
                    points.append((x, y))
                pygame.draw.polygon(shape_surf, color_with_alpha, points, 2)
                
            elif shape['type'] == 'hexagon':
                points = []
                for i in range(6):
                    angle = shape['rotation'] + i * math.pi / 3
                    x = current_size + math.cos(angle) * current_size * 0.8
                    y = current_size + math.sin(angle) * current_size * 0.8
                    points.append((x, y))
                pygame.draw.polygon(shape_surf, color_with_alpha, points, 2)
            
            screen.blit(shape_surf, (int(shape['x'] - current_size), int(shape['y'] - current_size)))

class MovingPlatform:
    def __init__(self, row, col, x, y, sound_generator, level):
        self.original_row = row
        self.original_col = col
        self.row = row
        self.col = col
        self.original_x = x
        self.original_y = y
        self.x = x
        self.y = y
        self.sound_generator = sound_generator
        self.level = level
        
        # Movement properties
        self.move_timer = 0
        self.move_interval = 2000  # Move every 2 seconds
        self.move_distance = 60    # Distance to move
        self.is_moving = False
        self.move_start_time = 0
        self.move_duration = 1000  # 1 second to complete move
        self.start_pos = (x, y)
        self.target_pos = (x, y)
        
        # Create the cube component
        self.cube = Cube(row, col, x, y, sound_generator, level)
        self.cube.cube_size = 45  # Slightly smaller for moving platforms
        
    def update(self, pyramid):
        """Update moving platform position"""
        current_time = pygame.time.get_ticks()
        
        if self.is_moving:
            # Currently moving
            elapsed = current_time - self.move_start_time
            if elapsed >= self.move_duration:
                # Movement complete
                self.is_moving = False
                self.x = self.target_pos[0]
                self.y = self.target_pos[1]
                self.cube.x = self.x
                self.cube.y = self.y
                self.move_timer = current_time
            else:
                # Interpolate position
                progress = elapsed / self.move_duration
                self.x = self.start_pos[0] + (self.target_pos[0] - self.start_pos[0]) * progress
                self.y = self.start_pos[1] + (self.target_pos[1] - self.start_pos[1]) * progress
                self.cube.x = self.x
                self.cube.y = self.y
        else:
            # Check if time to start moving
            if current_time - self.move_timer > self.move_interval:
                self.start_movement()
        
        # Update cube component
        self.cube.update()
    
    def start_movement(self):
        """Start moving to a new position"""
        import random
        
        # Choose random direction
        directions = [
            (self.move_distance, 0),    # Right
            (-self.move_distance, 0),   # Left
            (0, self.move_distance),    # Down
            (0, -self.move_distance)    # Up
        ]
        
        dx, dy = random.choice(directions)
        new_x = self.original_x + dx
        new_y = self.original_y + dy
        
        # Keep within reasonable bounds
        if 200 <= new_x <= SCREEN_WIDTH - 200 and 150 <= new_y <= SCREEN_HEIGHT - 200:
            self.start_pos = (self.x, self.y)
            self.target_pos = (new_x, new_y)
            self.is_moving = True
            self.move_start_time = pygame.time.get_ticks()
    
    def draw(self, screen):
        """Draw the moving platform with special indicator"""
        # Draw the cube
        self.cube.draw(screen)
        
        # Draw movement indicator (arrows around the cube)
        if not self.is_moving:
            arrow_color = (255, 255, 255, 100)
            arrow_size = 8
            # Draw small arrows indicating it can move
            for i in range(4):
                angle = i * math.pi / 2
                arrow_x = self.x + math.cos(angle) * 35
                arrow_y = self.y + math.sin(angle) * 35
                
                # Arrow points
                tip_x = arrow_x + math.cos(angle) * arrow_size
                tip_y = arrow_y + math.sin(angle) * arrow_size
                
                pygame.draw.line(screen, WHITE, (int(arrow_x), int(arrow_y)), 
                               (int(tip_x), int(tip_y)), 2)
    
    def step_on(self):
        """Handle stepping on moving platform"""
        return self.cube.step_on(self.particle_system, self.screen_shake)

class FlyingDisc:
    def __init__(self, x, y, sound_generator, side="left"):
        self.x = x
        self.y = y
        self.sound_generator = sound_generator
        self.side = side  # "left" or "right"
        self.size = 30
        self.active = True
        self.used = False
        self.qbert_on_disc = False
        self.transport_timer = 0
        self.transport_duration = 2000  # 2 seconds transport time
        self.start_pos = (x, y)
        self.target_pos = (x, y - 300)  # Fly upward off screen
        self.pulse_timer = 0
        self.rotation = 0
        
        # Multi-colored disc colors
        self.colors = [
            (255, 0, 0),    # Red
            (255, 128, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 255, 255),  # Cyan
            (0, 0, 255),    # Blue
            (128, 0, 255),  # Purple
            (255, 0, 255),  # Magenta
        ]
        
    def can_use(self, qbert_x, qbert_y):
        """Check if Q-Bert is close enough to use this disc"""
        if self.used:
            return False
        distance = math.sqrt((self.x - qbert_x)**2 + (self.y - qbert_y)**2)
        return distance < 80  # Increased range for easier access
        
    def activate_with_target(self, qbert_x, qbert_y, target_x, target_y):
        """Activate the flying disc with specific target coordinates"""
        if self.used:
            return False
            
        self.qbert_on_disc = True
        self.transport_timer = pygame.time.get_ticks()
        self.start_pos = (qbert_x, qbert_y)
        self.target_pos = (target_x, target_y)
        print(f"Flying disc activated: start=({qbert_x}, {qbert_y}), target=({target_x}, {target_y})")
        return True
        
    def activate(self, qbert_x, qbert_y):
        """Activate the flying disc to transport Q-Bert"""
        if self.used:
            return False
            
        self.qbert_on_disc = True
        self.transport_timer = pygame.time.get_ticks()
        self.start_pos = (qbert_x, qbert_y)
        # Transport to the exact center of the screen where the top cube should be
        # This matches the pyramid creation coordinates
        self.target_pos = (SCREEN_WIDTH // 2, 200)  # Center horizontally, appropriate height
        return True
        
    def update(self):
        """Update flying disc animation and transport"""
        if self.used:
            return False
            
        current_time = pygame.time.get_ticks()
        self.pulse_timer = current_time
        self.rotation += 3  # Rotate the disc
        
        if self.qbert_on_disc:
            elapsed = current_time - self.transport_timer
            if elapsed >= self.transport_duration:
                # Transport complete
                self.used = True
                self.qbert_on_disc = False
                return True  # Signal transport complete
            else:
                # Update position during transport (arc motion)
                progress = elapsed / self.transport_duration
                
                # Smooth easing function
                eased_progress = 1 - (1 - progress) ** 3
                
                # Arc motion - go up and then to target
                mid_x = (self.start_pos[0] + self.target_pos[0]) / 2
                mid_y = min(self.start_pos[1], self.target_pos[1]) - 100  # Arc height
                
                if progress < 0.5:
                    # First half - go to arc peak
                    arc_progress = progress * 2
                    self.x = self.start_pos[0] + (mid_x - self.start_pos[0]) * arc_progress
                    self.y = self.start_pos[1] + (mid_y - self.start_pos[1]) * arc_progress
                else:
                    # Second half - go from arc peak to target
                    arc_progress = (progress - 0.5) * 2
                    self.x = mid_x + (self.target_pos[0] - mid_x) * arc_progress
                    self.y = mid_y + (self.target_pos[1] - mid_y) * arc_progress
        
        return False
    
    def draw(self, screen):
        """Draw the multi-colored flying disc with retro styling"""
        if self.used:
            return
            
        # Pulsing effect
        pulse = abs(math.sin(self.pulse_timer * 0.005)) * 0.3 + 0.7
        current_size = int(self.size * pulse)
        
        # Draw multi-colored segments
        num_segments = len(self.colors)
        angle_per_segment = 360 / num_segments
        
        for i, color in enumerate(self.colors):
            start_angle = math.radians((i * angle_per_segment + self.rotation) % 360)
            end_angle = math.radians(((i + 1) * angle_per_segment + self.rotation) % 360)
            
            # Create points for the segment
            points = [(int(self.x), int(self.y))]
            
            # Add arc points
            for angle_step in range(int(angle_per_segment) + 1):
                angle = start_angle + (end_angle - start_angle) * (angle_step / angle_per_segment)
                px = self.x + math.cos(angle) * current_size
                py = self.y + math.sin(angle) * current_size
                points.append((int(px), int(py)))
            
            # Draw the segment
            if len(points) > 2:
                pygame.draw.polygon(screen, color, points)
        
        # Draw outer ring
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), current_size, 3)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), current_size, 1)
        
        # Draw inner circle
        inner_size = current_size // 3
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), inner_size)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), inner_size, 2)
        
        # Draw glow effect
        glow_size = current_size + 15
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        
        # Multi-colored glow
        for i, color in enumerate(self.colors):
            glow_alpha = int(30 + 20 * abs(math.sin(self.pulse_timer * 0.003 + i)))
            glow_color = (*color, glow_alpha)
            angle = math.radians(i * 45 + self.rotation)
            glow_x = glow_size + math.cos(angle) * 5
            glow_y = glow_size + math.sin(angle) * 5
            pygame.draw.circle(glow_surf, glow_color[:3], (int(glow_x), int(glow_y)), glow_size // 4)
        
        screen.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)))
    
    def get_qbert_position(self):
        """Get Q-Bert's position when on the disc"""
        return (self.x, self.y - 15)

class Enemy:
    def __init__(self, row, col, color, sound_generator):
        self.row = row
        self.col = col
        self.x = 0
        self.y = 0
        self.color = color
        self.size = 18
        self.sound_generator = sound_generator
        self.is_hopping = False
        self.hop_start_time = 0
        self.hop_duration = 400
        self.start_x = 0
        self.start_y = 0
        self.target_x = 0
        self.target_y = 0
        self.hop_height = 35
        self.last_move_time = 0
        self.move_delay = 600  # Slower than Q-Bert
        
        # Falling off board
        self.is_falling = False
        self.fall_start_time = 0
        self.fall_duration = 1200  # Slightly longer fall for enemies
        self.fall_start_y = 0
        
    def start_falling(self):
        """Start the falling off animation"""
        self.is_falling = True
        self.fall_start_time = pygame.time.get_ticks()
        self.fall_start_y = self.y
        
    def update_position(self, pyramid):
        """Update enemy's screen position based on current cube"""
        if self.row < len(pyramid) and self.col < len(pyramid[self.row]):
            cube = pyramid[self.row][self.col]
            self.x = cube.x
            self.y = cube.y - 35  # Position enemy above the larger cube
    
    def update(self):
        """Update enemy animation state"""
        # Handle falling animation
        if self.is_falling:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.fall_start_time
            
            if elapsed >= self.fall_duration:
                # Fall complete - enemy should be removed
                return "fall_complete"
            else:
                # Animate falling (accelerating downward)
                progress = elapsed / self.fall_duration
                fall_distance = 250 * progress * progress  # Quadratic fall
                self.y = self.fall_start_y + fall_distance
        
        # Handle normal hopping animation
        elif self.is_hopping:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.hop_start_time
            
            if elapsed >= self.hop_duration:
                self.is_hopping = False
                self.x = self.target_x
                self.y = self.target_y
            else:
                progress = elapsed / self.hop_duration
                self.x = self.start_x + (self.target_x - self.start_x) * progress
                base_y = self.start_y + (self.target_y - self.start_y) * progress
                hop_progress = 4 * progress * (1 - progress)
                self.y = base_y - (self.hop_height * hop_progress)
        
        return None
    
    def start_hop(self, target_x, target_y):
        """Start a hop animation to target position"""
        self.is_hopping = True
        self.hop_start_time = pygame.time.get_ticks()
        self.start_x = self.x
        self.start_y = self.y
        self.target_x = target_x
        self.target_y = target_y
    
    def can_move_to(self, new_row, new_col, pyramid):
        """Check if enemy can move to the specified position"""
        return (0 <= new_row < len(pyramid) and 
                0 <= new_col < len(pyramid[new_row]))
    
    def draw(self, screen):
        """Draw the enemy"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.size, 2)

class Coily(Enemy):
    def __init__(self, sound_generator, level=1):
        super().__init__(0, 0, NEON_PURPLE, sound_generator)  # Bright neon purple snake
        self.name = "Coily"
        # Base move delay starts even slower and gets faster with levels
        base_delay = 1800  # Start much slower (1.8 seconds)
        level_speedup = max(0, (level - 1) * 150)  # Reduce delay by 150ms per level
        self.move_delay = max(800, base_delay - level_speedup)  # Minimum 800ms delay
        
    def ai_move(self, qbert_row, qbert_col, pyramid, qbert_freeze_active=False):
        """Coily chases Q-Bert intelligently"""
        if self.is_hopping:
            return False
        
        # Don't move if Q-Bert has freeze power active
        if qbert_freeze_active:
            return False
            
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move_time < self.move_delay:
            return False
        
        # Calculate possible moves toward Q-Bert
        possible_moves = []
        
        # Down-left
        if self.can_move_to(self.row + 1, self.col, pyramid):
            possible_moves.append(("down_left", self.row + 1, self.col))
        
        # Down-right  
        if self.can_move_to(self.row + 1, self.col + 1, pyramid):
            possible_moves.append(("down_right", self.row + 1, self.col + 1))
        
        # Up-left
        if self.can_move_to(self.row - 1, self.col - 1, pyramid):
            possible_moves.append(("up_left", self.row - 1, self.col - 1))
        
        # Up-right
        if self.can_move_to(self.row - 1, self.col, pyramid):
            possible_moves.append(("up_right", self.row - 1, self.col))
        
        if not possible_moves:
            return False
        
        # Choose move that gets closest to Q-Bert
        best_move = None
        best_distance = float('inf')
        
        for move_name, new_row, new_col in possible_moves:
            # Calculate distance to Q-Bert
            distance = abs(new_row - qbert_row) + abs(new_col - qbert_col)
            if distance < best_distance:
                best_distance = distance
                best_move = (move_name, new_row, new_col)
        
        if best_move:
            move_name, new_row, new_col = best_move
            target_cube = pyramid[new_row][new_col]
            target_x = target_cube.x
            target_y = target_cube.y - 35  # Updated for larger cubes
            
            self.start_hop(target_x, target_y)
            self.row = new_row
            self.col = new_col
            self.last_move_time = current_time
            return True
        
        return False
    
    def draw(self, screen, particle_system):
        """Draw Coily as an enhanced detailed snake with authentic arcade styling"""
        # Add movement particles when hopping
        if self.is_hopping:
            current_time = pygame.time.get_ticks()
            if current_time % 80 < 40:  # Every 80ms, show for 40ms
                particle_system.add_sparks(self.x, self.y, self.color, 3)
        
        # Add falling effects
        if self.is_falling:
            particle_system.add_trail(self.x, self.y, (255, 0, 0), 4)  # Red trail when falling
        
        # Draw enhanced glow effect
        glow_size = self.size + 8
        glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (191, 64, 191, 80), (glow_size, glow_size), glow_size)
        screen.blit(glow_surf, (int(self.x - glow_size), int(self.y - glow_size)))
        
        # Draw snake body with enhanced segments
        body_size = self.size
        
        # Main body (largest segment) with texture
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), body_size)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), body_size, 3)
        
        # Enhanced snake pattern/scales on body
        scale_color = tuple(min(255, int(c * 1.4)) for c in self.color)
        darker_scale = tuple(int(c * 0.7) for c in self.color)
        
        # Diamond scale pattern
        for i in range(-1, 2):
            for j in range(-1, 2):
                if abs(i) + abs(j) == 1:  # Diamond pattern
                    scale_x = self.x + i * 8
                    scale_y = self.y + j * 6
                    pygame.draw.circle(screen, scale_color, (int(scale_x), int(scale_y)), 3)
                    pygame.draw.circle(screen, darker_scale, (int(scale_x), int(scale_y)), 2)
        
        # Enhanced snake head (more detailed and menacing)
        head_size = body_size + 4
        head_y = self.y - 5
        
        # Head with gradient
        for i in range(head_size):
            brightness = 1.0 - (i / head_size) * 0.3
            head_color = tuple(int(c * brightness) for c in self.color)
            pygame.draw.circle(screen, head_color, (int(self.x), int(head_y)), head_size - i, 1)
        
        pygame.draw.circle(screen, BLACK, (int(self.x), int(head_y)), head_size, 3)
        
        # Enhanced menacing snake eyes (larger and more detailed)
        eye_offset = 9
        eye_size = 6
        
        # Left eye with enhanced detail
        pygame.draw.circle(screen, RED, (int(self.x - eye_offset), int(head_y - 6)), eye_size)
        pygame.draw.circle(screen, BLACK, (int(self.x - eye_offset), int(head_y - 6)), eye_size, 2)
        # Vertical slit pupil (more pronounced)
        pygame.draw.ellipse(screen, BLACK, 
                          (int(self.x - eye_offset - 2), int(head_y - 9), 4, 6))
        # Menacing eye highlight
        pygame.draw.circle(screen, WHITE, (int(self.x - eye_offset + 2), int(head_y - 7)), 2)
        pygame.draw.circle(screen, RED, (int(self.x - eye_offset + 2), int(head_y - 7)), 1)
        
        # Right eye with enhanced detail
        pygame.draw.circle(screen, RED, (int(self.x + eye_offset), int(head_y - 6)), eye_size)
        pygame.draw.circle(screen, BLACK, (int(self.x + eye_offset), int(head_y - 6)), eye_size, 2)
        # Vertical slit pupil
        pygame.draw.ellipse(screen, BLACK, 
                          (int(self.x + eye_offset - 2), int(head_y - 9), 4, 6))
        # Menacing eye highlight
        pygame.draw.circle(screen, WHITE, (int(self.x + eye_offset - 2), int(head_y - 7)), 2)
        pygame.draw.circle(screen, RED, (int(self.x + eye_offset - 2), int(head_y - 7)), 1)
        
        # Enhanced snake mouth/fangs
        mouth_points = [
            (int(self.x - 4), int(head_y + 4)),
            (int(self.x), int(head_y + 10)),
            (int(self.x + 4), int(head_y + 4))
        ]
        pygame.draw.polygon(screen, BLACK, mouth_points)
        
        # Larger, more prominent fangs
        fang_points_left = [
            (int(self.x - 3), int(head_y + 5)),
            (int(self.x - 1), int(head_y + 5)),
            (int(self.x - 2), int(head_y + 9))
        ]
        fang_points_right = [
            (int(self.x + 1), int(head_y + 5)),
            (int(self.x + 3), int(head_y + 5)),
            (int(self.x + 2), int(head_y + 9))
        ]
        pygame.draw.polygon(screen, WHITE, fang_points_left)
        pygame.draw.polygon(screen, WHITE, fang_points_right)
        pygame.draw.polygon(screen, BLACK, fang_points_left, 1)
        pygame.draw.polygon(screen, BLACK, fang_points_right, 1)
        
        # Forked tongue (classic snake feature)
        if self.is_hopping:  # Show tongue when moving
            tongue_base_x = self.x
            tongue_base_y = head_y + 8
            tongue_length = 8
            
            # Tongue base
            pygame.draw.line(screen, (255, 100, 100), 
                           (int(tongue_base_x), int(tongue_base_y)),
                           (int(tongue_base_x), int(tongue_base_y + tongue_length)), 2)
            
            # Forked tip
            pygame.draw.line(screen, (255, 100, 100),
                           (int(tongue_base_x), int(tongue_base_y + tongue_length)),
                           (int(tongue_base_x - 3), int(tongue_base_y + tongue_length + 3)), 2)
            pygame.draw.line(screen, (255, 100, 100),
                           (int(tongue_base_x), int(tongue_base_y + tongue_length)),
                           (int(tongue_base_x + 3), int(tongue_base_y + tongue_length + 3)), 2)
        
        # Enhanced snake tail segments (more detailed)
        tail_segments = 3
        for i in range(tail_segments):
            segment_size = body_size - (i + 1) * 4
            segment_y = self.y + (i + 1) * 10
            if segment_size > 0:
                # Segment with gradient
                for j in range(segment_size):
                    brightness = 1.0 - (j / segment_size) * 0.4
                    segment_color = tuple(int(c * brightness) for c in self.color)
                    pygame.draw.circle(screen, segment_color, (int(self.x), int(segment_y)), segment_size - j, 1)
                
                pygame.draw.circle(screen, BLACK, (int(self.x), int(segment_y)), segment_size, 2)
                
                # Scale pattern on tail segments
                if segment_size > 6:
                    scale_x = self.x + (i % 2) * 4 - 2
                    pygame.draw.circle(screen, scale_color, (int(scale_x), int(segment_y)), 2)
        
        # Add coiling effect when falling
        if self.is_falling:
            # Draw spiral motion lines
            for i in range(6):
                angle = i * math.pi / 3 + (pygame.time.get_ticks() * 0.02)
                spiral_x = self.x + math.cos(angle) * (body_size + 10)
                spiral_y = self.y + math.sin(angle) * (body_size + 10)
                pygame.draw.circle(screen, (255, 0, 255, 100), (int(spiral_x), int(spiral_y)), 3)

class SoundGenerator:
    def __init__(self):
        self.sample_rate = 22050
        self.audio_available = AUDIO_AVAILABLE
        self.current_music_level = 0
        self.music_volume = 0.3
        self.sfx_volume = 0.5
        
    def generate_tone(self, frequency, duration, volume=0.3):
        """Generate a simple tone"""
        if not self.audio_available:
            return None
            
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            # Create a sine wave with slight decay for retro feel
            decay = 1.0 - (i / frames) * 0.3  # Slight volume decay
            wave = np.sin(2 * np.pi * frequency * i / self.sample_rate) * volume * decay
            arr[i] = [wave, wave]
        
        # Convert to pygame sound format
        arr = (arr * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        return sound
    
    def generate_hop_sound(self):
        """Generate Q-Bert's signature hop sound - a rising chirp"""
        if not self.audio_available:
            return None
            
        duration = 0.15  # Short sound
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        # Create a frequency sweep from low to high (like a hop)
        start_freq = 200
        end_freq = 400
        
        for i in range(frames):
            # Frequency increases over time (rising pitch)
            progress = i / frames
            frequency = start_freq + (end_freq - start_freq) * progress
            
            # Volume envelope - quick attack, gradual decay
            if progress < 0.1:
                volume = progress * 10  # Quick ramp up
            else:
                volume = 1.0 - ((progress - 0.1) / 0.9) * 0.7  # Gradual decay
            
            wave = np.sin(2 * np.pi * frequency * i / self.sample_rate) * volume * self.sfx_volume
            arr[i] = [wave, wave]
        
        # Convert to pygame sound format
        arr = (arr * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        return sound
    
    def generate_cube_change_sound(self):
        """Generate sound for when a cube changes color"""
        if not self.audio_available:
            return None
            
        duration = 0.1
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        # Simple descending tone
        start_freq = 600
        end_freq = 400
        
        for i in range(frames):
            progress = i / frames
            frequency = start_freq - (start_freq - end_freq) * progress
            volume = 1.0 - progress * 0.5  # Fade out
            
            wave = np.sin(2 * np.pi * frequency * i / self.sample_rate) * volume * self.sfx_volume
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        return sound
    
    def generate_coily_sound(self):
        """Generate Coily's menacing snake hiss"""
        if not self.audio_available:
            return None
            
        duration = 0.3
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        # Create a hissing sound with noise and low frequency
        import random
        for i in range(frames):
            # Base hiss frequency
            base_freq = 150 + 50 * math.sin(i * 0.01)
            
            # Add noise for hiss effect
            noise = (random.random() - 0.5) * 0.3
            
            # Combine sine wave with noise
            wave = (np.sin(2 * np.pi * base_freq * i / self.sample_rate) * 0.4 + noise) * self.sfx_volume
            
            # Volume envelope
            volume = 1.0 - (i / frames) * 0.6
            arr[i] = [wave * volume, wave * volume]
        
        arr = np.clip(arr * 32767, -32767, 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        return sound
    
    def generate_power_up_sound(self):
        """Generate power-up collection sound"""
        if not self.audio_available:
            return None
            
        duration = 0.4
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        # Ascending arpeggio
        frequencies = [440, 554, 659, 880]  # A major chord
        
        for i in range(frames):
            progress = i / frames
            freq_index = int(progress * len(frequencies))
            if freq_index >= len(frequencies):
                freq_index = len(frequencies) - 1
                
            frequency = frequencies[freq_index]
            volume = 1.0 - progress * 0.3
            
            wave = np.sin(2 * np.pi * frequency * i / self.sample_rate) * volume * self.sfx_volume
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        return sound
    
    def generate_level_complete_fanfare(self):
        """Generate victory fanfare for level completion"""
        if not self.audio_available:
            return None
            
        duration = 2.0  # Longer fanfare
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        # Victory melody - classic arcade style
        melody = [
            (523, 0.2),  # C
            (659, 0.2),  # E
            (784, 0.2),  # G
            (1047, 0.4), # C (octave)
            (784, 0.2),  # G
            (1047, 0.6)  # C (octave) - held
        ]
        
        current_frame = 0
        for freq, note_duration in melody:
            note_frames = int(note_duration * self.sample_rate)
            
            for i in range(note_frames):
                if current_frame + i >= frames:
                    break
                    
                # Note envelope
                note_progress = i / note_frames
                if note_progress < 0.1:
                    volume = note_progress * 10
                else:
                    volume = 1.0 - ((note_progress - 0.1) / 0.9) * 0.5
                
                wave = np.sin(2 * np.pi * freq * (current_frame + i) / self.sample_rate) * volume * self.sfx_volume
                arr[current_frame + i] = [wave, wave]
            
            current_frame += note_frames
        
        arr = (arr * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        return sound
    
    def generate_background_music(self, level):
        """Generate new wave/electronic 80s background music based on level theme"""
        if not self.audio_available:
            return None
            
        # New Wave/Electronic 80s style music with different progressions
        music_data = {
            1: {  # Neon Dreams - New Wave style
                'chords': [(220, 293, 349), (196, 261, 311), (233, 293, 369), (220, 293, 349)],
                'bass_line': [110, 98, 116, 110],
                'lead_melody': [440, 523, 587, 523, 440, 392, 349, 392],
                'drum_pattern': [1, 0, 1, 0, 1, 0, 1, 1],  # Electronic drum pattern
                'tempo': 0.4
            },
            2: {  # Cyber Pulse - Driving electronic
                'chords': [(261, 329, 392), (246, 311, 369), (277, 349, 415), (261, 329, 392)],
                'bass_line': [130, 123, 138, 130],
                'lead_melody': [523, 659, 698, 659, 523, 466, 415, 466],
                'drum_pattern': [1, 1, 0, 1, 1, 0, 1, 0],
                'tempo': 0.35
            },
            3: {  # Digital Rain - Atmospheric
                'chords': [(174, 220, 261), (196, 246, 293), (220, 277, 329), (174, 220, 261)],
                'bass_line': [87, 98, 110, 87],
                'lead_melody': [349, 440, 523, 440, 349, 311, 277, 311],
                'drum_pattern': [1, 0, 0, 1, 1, 0, 0, 1],
                'tempo': 0.5
            },
            4: {  # Retro Future - Upbeat electronic
                'chords': [(293, 369, 440), (329, 415, 493), (277, 349, 415), (293, 369, 440)],
                'bass_line': [146, 164, 138, 146],
                'lead_melody': [587, 698, 784, 698, 587, 523, 466, 523],
                'drum_pattern': [1, 0, 1, 1, 1, 0, 1, 0],
                'tempo': 0.3
            },
            5: {  # Neon Nights - Dark electronic
                'chords': [(155, 196, 233), (174, 220, 261), (196, 246, 293), (155, 196, 233)],
                'bass_line': [77, 87, 98, 77],
                'lead_melody': [311, 392, 466, 392, 311, 277, 246, 277],
                'drum_pattern': [1, 1, 0, 0, 1, 1, 0, 1],
                'tempo': 0.45
            },
            6: {  # Electric Dreams - Melodic electronic
                'chords': [(246, 311, 369), (277, 349, 415), (311, 392, 466), (246, 311, 369)],
                'bass_line': [123, 138, 155, 123],
                'lead_melody': [493, 622, 740, 622, 493, 440, 392, 440],
                'drum_pattern': [1, 0, 1, 0, 1, 1, 0, 1],
                'tempo': 0.4
            }
        }
        
        theme_num = ((level - 1) % 6) + 1
        music_info = music_data.get(theme_num, music_data[1])
        
        duration = 16.0  # Longer tracks for more complex arrangements
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        chord_duration = duration / len(music_info['chords'])
        beat_duration = chord_duration / len(music_info['drum_pattern'])
        
        for chord_idx, (chord, bass_freq) in enumerate(zip(music_info['chords'], music_info['bass_line'])):
            start_frame = int(chord_idx * chord_duration * self.sample_rate)
            end_frame = int((chord_idx + 1) * chord_duration * self.sample_rate)
            
            freq1, freq2, freq3 = chord
            
            for i in range(start_frame, min(end_frame, frames)):
                # New Wave style chord pads (softer, more atmospheric)
                pad1 = np.sin(2 * np.pi * freq1 * i / self.sample_rate) * 0.12
                pad2 = np.sin(2 * np.pi * freq2 * i / self.sample_rate) * 0.10
                pad3 = np.sin(2 * np.pi * freq3 * i / self.sample_rate) * 0.10
                
                # Electronic bass line (more prominent)
                bass_wave = np.sin(2 * np.pi * bass_freq * i / self.sample_rate) * 0.3
                # Add bass harmonics for richer sound
                bass_harmonic = np.sin(2 * np.pi * (bass_freq * 2) * i / self.sample_rate) * 0.1
                
                # Lead synthesizer melody
                melody_progress = ((i - start_frame) / self.sample_rate) % (len(music_info['lead_melody']) * beat_duration)
                melody_index = int(melody_progress / beat_duration)
                if melody_index < len(music_info['lead_melody']):
                    lead_freq = music_info['lead_melody'][melody_index]
                    # Square wave for classic 80s synth sound
                    lead_wave = np.sign(np.sin(2 * np.pi * lead_freq * i / self.sample_rate)) * 0.15
                    # Add slight detuning for chorus effect
                    lead_chorus = np.sign(np.sin(2 * np.pi * (lead_freq * 1.01) * i / self.sample_rate)) * 0.08
                else:
                    lead_wave = 0
                    lead_chorus = 0
                
                # Electronic drum pattern
                beat_progress = ((i - start_frame) / self.sample_rate) % (len(music_info['drum_pattern']) * beat_duration)
                beat_index = int(beat_progress / beat_duration)
                if beat_index < len(music_info['drum_pattern']) and music_info['drum_pattern'][beat_index]:
                    # Kick drum (low frequency pulse)
                    kick_freq = 60 + 40 * np.sin(i * 0.001)
                    kick = np.sin(2 * np.pi * kick_freq * i / self.sample_rate) * 0.2
                    # Hi-hat (high frequency noise)
                    hihat = np.random.random() * 0.05 if (i % (self.sample_rate // 8)) < (self.sample_rate // 32) else 0
                else:
                    kick = 0
                    hihat = 0
                
                # Add subtle filter sweep (classic 80s effect)
                filter_freq = 0.0001 + 0.00005 * np.sin(i * 0.0001)
                filter_mod = 0.7 + 0.3 * np.sin(i * filter_freq)
                
                # Combine all elements
                combined = (pad1 + pad2 + pad3 + bass_wave + bass_harmonic + 
                           lead_wave + lead_chorus + kick + hihat) * self.music_volume
                
                # Apply filter and slight reverb effect
                combined *= filter_mod
                if i > self.sample_rate // 4:  # Add reverb delay
                    reverb = arr[i - self.sample_rate // 4][0] * 0.1
                    combined += reverb
                
                arr[i] = [combined, combined]
        
        arr = np.clip(arr * 32767, -32767, 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        return sound
    
    def generate_ambient_atmosphere(self):
        """Generate subtle electronic ambient atmosphere"""
        if not self.audio_available:
            return None
            
        duration = 10.0  # Long ambient loop
        frames = int(duration * self.sample_rate)
        arr = np.zeros((frames, 2))
        
        # Create subtle electronic pad sounds
        for i in range(frames):
            # Very low frequency pad
            pad1 = np.sin(2 * np.pi * 60 * i / self.sample_rate) * 0.1
            pad2 = np.sin(2 * np.pi * 80 * i / self.sample_rate) * 0.08
            
            # Add subtle high frequency sparkle
            sparkle = np.sin(2 * np.pi * 2000 * i / self.sample_rate) * 0.02 * abs(np.sin(i * 0.001))
            
            # Combine with very low volume
            combined = (pad1 + pad2 + sparkle) * 0.15
            arr[i] = [combined, combined]
        
        arr = (arr * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        return sound

class AudioManager:
    def __init__(self, sound_generator):
        self.sound_generator = sound_generator
        self.current_music = None
        self.current_ambient = None
        self.current_level = 0
        self.music_channel = None
        self.ambient_channel = None
        
        # Initialize pygame mixer channels
        if sound_generator.audio_available:
            pygame.mixer.set_num_channels(8)  # More channels for layered audio
            self.music_channel = pygame.mixer.Channel(0)
            self.ambient_channel = pygame.mixer.Channel(1)
    
    def play_background_music(self, level):
        """Play background music for the current level theme"""
        if not self.sound_generator.audio_available:
            return
            
        # Only change music if level theme changed
        theme_num = ((level - 1) % 6) + 1
        current_theme = ((self.current_level - 1) % 6) + 1 if self.current_level > 0 else 0
        
        if theme_num != current_theme:
            # Stop current music
            if self.music_channel and self.music_channel.get_busy():
                self.music_channel.stop()
            
            # Generate and play new music
            music = self.sound_generator.generate_background_music(level)
            if music:
                self.current_music = music
                self.current_level = level
                if self.music_channel:
                    self.music_channel.play(music, loops=-1)  # Loop indefinitely
    
    def play_ambient_atmosphere(self):
        """Play subtle ambient atmosphere"""
        if not self.sound_generator.audio_available:
            return
            
        if not self.ambient_channel or not self.ambient_channel.get_busy():
            ambient = self.sound_generator.generate_ambient_atmosphere()
            if ambient and self.ambient_channel:
                self.current_ambient = ambient
                self.ambient_channel.play(ambient, loops=-1)  # Loop indefinitely
    
    def play_level_complete_fanfare(self):
        """Play victory fanfare when level is completed"""
        if not self.sound_generator.audio_available:
            return
            
        # Temporarily stop background music for fanfare
        if self.music_channel and self.music_channel.get_busy():
            self.music_channel.pause()
        
        fanfare = self.sound_generator.generate_level_complete_fanfare()
        if fanfare:
            # Play fanfare on a separate channel
            fanfare_channel = pygame.mixer.Channel(2)
            fanfare_channel.play(fanfare)
            
            # Resume background music after fanfare (2 seconds)
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000)
    
    def resume_background_music(self):
        """Resume background music after fanfare"""
        if self.music_channel:
            self.music_channel.unpause()
    
    def play_power_up_sound(self):
        """Play power-up collection sound"""
        if not self.sound_generator.audio_available:
            return
            
        power_up_sound = self.sound_generator.generate_power_up_sound()
        if power_up_sound:
            # Play on available channel
            pygame.mixer.Channel(3).play(power_up_sound)
    
    def play_enemy_sound(self, enemy_type):
        """Play enemy-specific sound"""
        if not self.sound_generator.audio_available:
            return
            
        if enemy_type == "coily":
            enemy_sound = self.sound_generator.generate_coily_sound()
            if enemy_sound:
                pygame.mixer.Channel(4).play(enemy_sound)
    
    def stop_all_music(self):
        """Stop all background music and ambient sounds"""
        if self.music_channel:
            self.music_channel.stop()
        if self.ambient_channel:
            self.ambient_channel.stop()
    
    def set_music_volume(self, volume):
        """Set background music volume (0.0 to 1.0)"""
        self.sound_generator.music_volume = volume
        if self.music_channel:
            self.music_channel.set_volume(volume)
    
    def set_sfx_volume(self, volume):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sound_generator.sfx_volume = volume

class ProgressionSystem:
    def __init__(self):
        self.save_file = "qbert_progress.json"
        self.data = self.load_progress()
        
        # Initialize default data structure
        if not self.data:
            self.data = {
                "high_scores": [],
                "statistics": {
                    "games_played": 0,
                    "total_hops": 0,
                    "enemies_defeated": 0,
                    "power_ups_collected": 0,
                    "cubes_changed": 0,
                    "total_playtime": 0,
                    "highest_level": 1
                },
                "achievements": {},
                "unlocked_themes": [1, 2, 3, 4, 5, 6],  # Default themes
                "unlocked_bonus_themes": []
            }
        
        # Achievement definitions
        self.achievement_definitions = {
            "first_steps": {
                "name": "First Steps",
                "description": "Complete your first level",
                "condition": lambda stats: stats.get("highest_level", 1) >= 2,
                "reward": "Bronze Trophy"
            },
            "perfect_level": {
                "name": "Perfect Level",
                "description": "Complete a level without losing a life",
                "condition": lambda stats: stats.get("perfect_levels", 0) >= 1,
                "reward": "Precision Master Badge"
            },
            "speed_demon": {
                "name": "Speed Demon",
                "description": "Complete a level in under 30 seconds",
                "condition": lambda stats: stats.get("fastest_level", 999) <= 30,
                "reward": "Lightning Theme"
            },
            "survivor": {
                "name": "Survivor",
                "description": "Reach level 10",
                "condition": lambda stats: stats.get("highest_level", 1) >= 10,
                "reward": "Survivor Theme"
            },
            "hop_master": {
                "name": "Hop Master",
                "description": "Make 1000 total hops",
                "condition": lambda stats: stats.get("total_hops", 0) >= 1000,
                "reward": "Golden Q-Bert"
            },
            "snake_slayer": {
                "name": "Snake Slayer",
                "description": "Defeat 50 Coily enemies",
                "condition": lambda stats: stats.get("enemies_defeated", 0) >= 50,
                "reward": "Warrior Theme"
            },
            "power_collector": {
                "name": "Power Collector",
                "description": "Collect 100 power-ups",
                "condition": lambda stats: stats.get("power_ups_collected", 0) >= 100,
                "reward": "Mystic Theme"
            },
            "cube_master": {
                "name": "Cube Master",
                "description": "Change 5000 cube colors",
                "condition": lambda stats: stats.get("cubes_changed", 0) >= 5000,
                "reward": "Rainbow Theme"
            },
            "marathon_runner": {
                "name": "Marathon Runner",
                "description": "Play for 1 hour total",
                "condition": lambda stats: stats.get("total_playtime", 0) >= 3600,
                "reward": "Endurance Theme"
            },
            "legend": {
                "name": "Q-Bert Legend",
                "description": "Reach level 25",
                "condition": lambda stats: stats.get("highest_level", 1) >= 25,
                "reward": "Legendary Theme"
            }
        }
        
        # Bonus theme definitions
        self.bonus_themes = {
            7: {  # Lightning Theme
                'original_top': (255, 255, 0),
                'original_left': (200, 200, 0),
                'original_right': (150, 150, 0),
                'original_edge': (255, 255, 100),
                'target_top': (255, 255, 255),
                'target_left': (255, 255, 200),
                'target_right': (200, 200, 150),
                'target_edge': (255, 255, 255),
                'explosion_colors': [(255, 255, 255), (255, 255, 0), (255, 200, 0), (255, 150, 0), (255, 100, 0)]
            },
            8: {  # Survivor Theme
                'original_top': (100, 50, 0),
                'original_left': (80, 40, 0),
                'original_right': (60, 30, 0),
                'original_edge': (120, 60, 0),
                'target_top': (255, 100, 0),
                'target_left': (255, 150, 50),
                'target_right': (200, 100, 0),
                'target_edge': (255, 200, 100),
                'explosion_colors': [(255, 255, 255), (255, 100, 0), (255, 50, 0), (200, 0, 0), (150, 0, 0)]
            },
            9: {  # Warrior Theme
                'original_top': (100, 0, 0),
                'original_left': (80, 0, 0),
                'original_right': (60, 0, 0),
                'original_edge': (120, 0, 0),
                'target_top': (255, 0, 0),
                'target_left': (255, 50, 50),
                'target_right': (200, 0, 0),
                'target_edge': (255, 100, 100),
                'explosion_colors': [(255, 255, 255), (255, 0, 0), (200, 0, 0), (150, 0, 0), (100, 0, 0)]
            },
            10: {  # Mystic Theme
                'original_top': (50, 0, 100),
                'original_left': (40, 0, 80),
                'original_right': (30, 0, 60),
                'original_edge': (60, 0, 120),
                'target_top': (150, 0, 255),
                'target_left': (200, 50, 255),
                'target_right': (100, 0, 200),
                'target_edge': (200, 100, 255),
                'explosion_colors': [(255, 255, 255), (150, 0, 255), (100, 0, 200), (50, 0, 150), (25, 0, 100)]
            },
            11: {  # Rainbow Theme
                'original_top': (128, 128, 128),
                'original_left': (100, 100, 100),
                'original_right': (80, 80, 80),
                'original_edge': (150, 150, 150),
                'target_top': (255, 128, 255),
                'target_left': (255, 200, 128),
                'target_right': (128, 255, 200),
                'target_edge': (200, 255, 255),
                'explosion_colors': [(255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255)]
            },
            12: {  # Endurance Theme
                'original_top': (0, 100, 100),
                'original_left': (0, 80, 80),
                'original_right': (0, 60, 60),
                'original_edge': (0, 120, 120),
                'target_top': (0, 255, 255),
                'target_left': (50, 255, 255),
                'target_right': (0, 200, 200),
                'target_edge': (100, 255, 255),
                'explosion_colors': [(255, 255, 255), (0, 255, 255), (0, 200, 255), (0, 150, 255), (0, 100, 255)]
            },
            13: {  # Legendary Theme
                'original_top': (50, 50, 50),
                'original_left': (40, 40, 40),
                'original_right': (30, 30, 30),
                'original_edge': (70, 70, 70),
                'target_top': (255, 215, 0),  # Gold
                'target_left': (255, 235, 50),
                'target_right': (200, 170, 0),
                'target_edge': (255, 255, 100),
                'explosion_colors': [(255, 255, 255), (255, 215, 0), (255, 200, 0), (255, 150, 0), (200, 100, 0)]
            }
        }
    
    def load_progress(self):
        """Load progress from save file"""
        try:
            import json
            import os
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Could not load progress: {e}")
        return None
    
    def save_progress(self):
        """Save progress to file"""
        try:
            import json
            with open(self.save_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Could not save progress: {e}")
    
    def add_high_score(self, score, level, name="Player"):
        """Add a new high score"""
        import time
        score_entry = {
            "score": score,
            "level": level,
            "name": name,
            "date": time.strftime("%Y-%m-%d %H:%M")
        }
        
        self.data["high_scores"].append(score_entry)
        self.data["high_scores"].sort(key=lambda x: x["score"], reverse=True)
        self.data["high_scores"] = self.data["high_scores"][:10]  # Keep top 10
        self.save_progress()
    
    def update_statistics(self, **kwargs):
        """Update game statistics"""
        for key, value in kwargs.items():
            if key in self.data["statistics"]:
                if key in ["highest_level", "fastest_level"]:
                    # For these, we want the best (highest level, fastest time)
                    if key == "highest_level":
                        self.data["statistics"][key] = max(self.data["statistics"][key], value)
                    elif key == "fastest_level":
                        self.data["statistics"][key] = min(self.data["statistics"].get(key, 999), value)
                else:
                    # For counters, add to existing value
                    self.data["statistics"][key] += value
            else:
                # New statistic
                self.data["statistics"][key] = value
        
        self.check_achievements()
        self.save_progress()
    
    def check_achievements(self):
        """Check and unlock achievements"""
        newly_unlocked = []
        
        for achievement_id, achievement in self.achievement_definitions.items():
            if achievement_id not in self.data["achievements"]:
                if achievement["condition"](self.data["statistics"]):
                    self.data["achievements"][achievement_id] = {
                        "unlocked": True,
                        "date": __import__('time').strftime("%Y-%m-%d %H:%M")
                    }
                    newly_unlocked.append(achievement)
                    
                    # Unlock bonus themes
                    if "Theme" in achievement["reward"]:
                        theme_id = self.get_theme_id_from_reward(achievement["reward"])
                        if theme_id and theme_id not in self.data["unlocked_themes"]:
                            self.data["unlocked_bonus_themes"].append(theme_id)
        
        return newly_unlocked
    
    def spawn_flying_disc(self):
        """Spawn flying disc when Q-Bert is in danger"""
        current_time = pygame.time.get_ticks()
        
        # Check if Q-Bert is in danger (enemy nearby)
        if self.is_qbert_in_danger() and current_time - self.disc_spawn_timer > self.disc_spawn_delay:
            # Spawn disc near Q-Bert's current position
            qbert_cube = self.pyramid[self.qbert.row][self.qbert.col]
            disc_x = qbert_cube.x + 60  # Slightly to the side
            disc_y = qbert_cube.y
            
            flying_disc = FlyingDisc(disc_x, disc_y, self.sound_generator)
            flying_disc.spawn_time = current_time  # Set spawn time
            self.flying_discs.append(flying_disc)
            self.disc_spawn_timer = current_time
    
    def is_qbert_in_danger(self):
        """Check if Q-Bert is in immediate danger from enemies"""
        qbert_row, qbert_col = self.qbert.row, self.qbert.col
        
        for enemy in self.enemies:
            # Check if enemy is close (within 2 moves)
            distance = abs(enemy.row - qbert_row) + abs(enemy.col - qbert_col)
            if distance <= 2:
                return True
        return False
    
    def handle_character_updates(self):
        """Handle Q-Bert and enemy updates including falling"""
        # Update Q-Bert
        qbert_result = self.qbert.update()
        
        if qbert_result == "transport_complete":
            # Q-Bert transported back to safety - reset to top
            self.qbert.row = 0
            self.qbert.col = 0
            self.qbert.update_position(self.pyramid)
        elif qbert_result == "fall_complete":
            # Q-Bert fell off - lose life
            self.lives -= 1
            self.level_perfect = False
            if self.lives <= 0:
                self.game_over = True
                self.end_game()
            else:
                self.reset_positions()
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy_result = enemy.update()
            if enemy_result == "fall_complete":
                # Enemy fell off - remove it
                self.enemies.remove(enemy)
                # Award points for enemy falling off
                self.score += 25
                self.progression_system.update_statistics(enemies_defeated=1)
    
    def get_theme_id_from_reward(self, reward):
        """Get theme ID from reward name"""
        theme_map = {
            "Lightning Theme": 7,
            "Survivor Theme": 8,
            "Warrior Theme": 9,
            "Mystic Theme": 10,
            "Rainbow Theme": 11,
            "Endurance Theme": 12,
            "Legendary Theme": 13
        }
        return theme_map.get(reward)
    
    def get_available_themes(self):
        """Get all available themes (default + unlocked bonus)"""
        return self.data["unlocked_themes"] + self.data["unlocked_bonus_themes"]
    
    def get_high_scores(self):
        """Get high scores list"""
        return self.data["high_scores"]
    
    def get_statistics(self):
        """Get game statistics"""
        return self.data["statistics"]
    
    def get_achievements(self):
        """Get unlocked achievements"""
        return self.data["achievements"]

class Cube:
    def __init__(self, row, col, x, y, sound_generator, level=1, progression_system=None):
        self.row = row
        self.col = col
        self.x = x
        self.y = y
        self.sound_generator = sound_generator
        self.cube_size = 50  # Larger cubes for better 3D effect
        self.cube_height = 30  # Height of the 3D cube
        self.level = level
        self.progression_system = progression_system
        
        # Multi-color cube system (Level 3+)
        self.max_steps = 1 if level < 3 else min(3, 1 + (level - 3) // 2)  # 1-3 steps needed
        self.current_step = 0
        self.is_complete = False
        
        # Get color scheme for current level
        self.color_scheme = get_color_scheme(level, progression_system)
        
        # Multi-step colors
        self.step_colors = self.generate_step_colors()
        
        # 3D cube colors with sharp contrast
        self.top_color = self.step_colors[0]['top']
        self.left_color = self.step_colors[0]['left']
        self.right_color = self.step_colors[0]['right']
        self.edge_color = self.step_colors[0]['edge']
        
        # Explosion effect
        self.explosion_timer = 0
        self.explosion_duration = 300  # 300ms explosion effect
        self.is_exploding = False
        
    def generate_step_colors(self):
        """Generate colors for each step of the cube progression"""
        colors = []
        
        # Step 0: Original colors
        colors.append({
            'top': self.color_scheme['original_top'],
            'left': self.color_scheme['original_left'],
            'right': self.color_scheme['original_right'],
            'edge': self.color_scheme['original_edge']
        })
        
        if self.max_steps > 1:
            # Step 1: Intermediate color (blend of original and target)
            orig = self.color_scheme['original_top']
            target = self.color_scheme['target_top']
            blend_top = tuple(max(0, min(255, int(orig[i] + (target[i] - orig[i]) * 0.5))) for i in range(3))
            
            orig_left = self.color_scheme['original_left']
            target_left = self.color_scheme['target_left']
            blend_left = tuple(max(0, min(255, int(orig_left[i] + (target_left[i] - orig_left[i]) * 0.5))) for i in range(3))
            
            colors.append({
                'top': blend_top,
                'left': blend_left,
                'right': tuple(max(0, min(255, int(c * 0.8))) for c in blend_left),
                'edge': tuple(max(0, min(255, int(c * 1.2))) for c in blend_top)
            })
        
        if self.max_steps > 2:
            # Step 2: Almost target color
            target = self.color_scheme['target_top']
            almost_target = tuple(max(0, min(255, int(c * 0.9))) for c in target)
            
            colors.append({
                'top': almost_target,
                'left': tuple(max(0, min(255, int(c * 0.8))) for c in target),
                'right': tuple(max(0, min(255, int(c * 0.7))) for c in target),
                'edge': tuple(max(0, min(255, int(c * 1.1))) for c in target)
            })
        
        # Final step: Target colors
        colors.append({
            'top': self.color_scheme['target_top'],
            'left': self.color_scheme['target_left'],
            'right': self.color_scheme['target_right'],
            'edge': self.color_scheme['target_edge']
        })
        
        return colors
        
    def update_color_scheme(self, level, progression_system=None):
        """Update colors when level changes"""
        self.level = level
        self.progression_system = progression_system
        self.color_scheme = get_color_scheme(level, progression_system)
        
        # Reset multi-step system for new level
        self.max_steps = 1 if level < 3 else min(3, 1 + (level - 3) // 2)
        self.current_step = 0
        self.is_complete = False
        self.step_colors = self.generate_step_colors()
        
        # Update current colors
        self.top_color = self.step_colors[self.current_step]['top']
        self.left_color = self.step_colors[self.current_step]['left']
        self.right_color = self.step_colors[self.current_step]['right']
        self.edge_color = self.step_colors[self.current_step]['edge']
        
    def step_on(self, particle_system=None, screen_shake=None):
        """Change cube color when stepped on with multi-step progression"""
        if not self.is_complete:
            self.current_step += 1
            
            if self.current_step >= self.max_steps:
                # Cube is now complete
                self.is_complete = True
                self.current_step = self.max_steps
            
            # Update colors to next step
            step_index = min(self.current_step, len(self.step_colors) - 1)
            self.top_color = self.step_colors[step_index]['top']
            self.left_color = self.step_colors[step_index]['left']
            self.right_color = self.step_colors[step_index]['right']
            self.edge_color = self.step_colors[step_index]['edge']
            
            # Start explosion effect
            self.is_exploding = True
            self.explosion_timer = pygame.time.get_ticks()
            
            # Add particle effects
            if particle_system:
                particle_system.add_explosion(self.x, self.y - 15, self.top_color, 12)
                if self.is_complete:
                    # Extra particles for completion
                    particle_system.add_sparks(self.x, self.y - 15, WHITE, 8)
            
            # Add screen shake
            if screen_shake:
                intensity = 3 if self.is_complete else 2
                screen_shake.add_shake(10, intensity)
            
            # Play cube change sound if available
            cube_sound = self.sound_generator.generate_cube_change_sound()
            if cube_sound:
                cube_sound.play()
            
            return True
        return False
    
    def update(self):
        """Update explosion animation"""
        if self.is_exploding:
            current_time = pygame.time.get_ticks()
            if current_time - self.explosion_timer > self.explosion_duration:
                self.is_exploding = False
    
    def draw(self, screen):
        """Draw the cube in proper 3D with connected appearance"""
        # Calculate 3D cube dimensions
        w = self.cube_size
        h = self.cube_height
        
        # Base position
        base_x = self.x
        base_y = self.y
        
        # 3D cube vertices
        # Top face vertices (rhombus)
        top_vertices = [
            (base_x, base_y - h),                    # Top point
            (base_x + w//2, base_y - h//2),          # Right point
            (base_x, base_y),                        # Bottom point
            (base_x - w//2, base_y - h//2)           # Left point
        ]
        
        # Left face vertices (parallelogram)
        left_vertices = [
            (base_x - w//2, base_y - h//2),          # Top-left
            (base_x, base_y),                        # Top-right
            (base_x, base_y + h//2),                 # Bottom-right
            (base_x - w//2, base_y)                  # Bottom-left
        ]
        
        # Right face vertices (parallelogram)
        right_vertices = [
            (base_x, base_y),                        # Top-left
            (base_x + w//2, base_y - h//2),          # Top-right
            (base_x + w//2, base_y),                 # Bottom-right
            (base_x, base_y + h//2)                  # Bottom-left
        ]
        
        # Draw explosion effect if active
        if self.is_exploding:
            current_time = pygame.time.get_ticks()
            progress = (current_time - self.explosion_timer) / self.explosion_duration
            
            # Create pulsing explosion effect with level-specific colors
            explosion_size = int(20 * (1 - progress))
            if explosion_size > 0:
                explosion_colors = self.color_scheme['explosion_colors']
                for i, color in enumerate(explosion_colors):
                    size = explosion_size - i * 3
                    if size > 0:
                        pygame.draw.circle(screen, color, (int(base_x), int(base_y - h//2)), size)
        
        # Draw the cube faces in correct order (back to front)
        
        # 1. Draw right face (back-right)
        pygame.draw.polygon(screen, self.right_color, right_vertices)
        
        # 2. Draw left face (back-left)  
        pygame.draw.polygon(screen, self.left_color, left_vertices)
        
        # 3. Draw top face (front)
        pygame.draw.polygon(screen, self.top_color, top_vertices)
        
        # Draw sharp edges for 3D effect
        pygame.draw.polygon(screen, self.edge_color, top_vertices, 3)
        pygame.draw.polygon(screen, self.edge_color, left_vertices, 2)
        pygame.draw.polygon(screen, self.edge_color, right_vertices, 2)
        
        # Add connecting lines between faces for solid 3D look
        # Vertical edges
        pygame.draw.line(screen, self.edge_color, 
                        (base_x - w//2, base_y - h//2), 
                        (base_x - w//2, base_y), 2)
        pygame.draw.line(screen, self.edge_color, 
                        (base_x + w//2, base_y - h//2), 
                        (base_x + w//2, base_y), 2)
        pygame.draw.line(screen, self.edge_color, 
                        (base_x, base_y), 
                        (base_x, base_y + h//2), 2)
        
        # Add intense neon glow for activated cubes
        if self.is_complete:
            # Multiple glow layers for intense effect using level colors
            target_color = self.color_scheme['target_top']
            for i in range(3):
                glow_size = 15 + i * 8
                alpha = 80 - i * 20
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*target_color, alpha), 
                                 (glow_size, glow_size), glow_size)
                screen.blit(glow_surf, (int(base_x - glow_size), int(base_y - h//2 - glow_size)))
            
            # Sharp highlight on edges
            pygame.draw.polygon(screen, WHITE, top_vertices, 1)
        elif self.current_step > 0:
            # Partial glow for intermediate steps
            current_color = self.top_color
            glow_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*current_color, 40), (15, 15), 15)
            screen.blit(glow_surf, (int(base_x - 15), int(base_y - h//2 - 15)))

class HomeScreen:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.animated_background = AnimatedBackground(width, height)
        self.title_pulse = 0
        self.subtitle_pulse = 0
        self.instruction_pulse = 0
        
    def update(self):
        """Update home screen animations"""
        self.animated_background.update()
        self.title_pulse += 0.05
        self.subtitle_pulse += 0.03
        self.instruction_pulse += 0.08
    
    def draw_graffiti_text(self, screen, text, x, y, base_size, colors, pulse_offset=0):
        """Draw graffiti-style neon text with multiple layers"""
        pulse = abs(math.sin(self.title_pulse + pulse_offset)) * 0.3 + 0.7
        current_size = int(base_size * pulse)
        
        # Create font (use default pygame font but make it bold-looking with multiple draws)
        font = pygame.font.Font(None, current_size)
        
        # Draw multiple layers for graffiti effect
        layers = [
            (colors[0], 6),  # Outer glow
            (colors[1], 4),  # Middle glow  
            (colors[2], 2),  # Inner glow
            (colors[3], 0),  # Core text
        ]
        
        for color, offset in layers:
            # Create text surface
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(x, y))
            
            # Draw with offset for 3D effect
            for dx in range(-offset, offset + 1):
                for dy in range(-offset, offset + 1):
                    if dx == 0 and dy == 0 and offset > 0:
                        continue
                    screen.blit(text_surface, (text_rect.x + dx, text_rect.y + dy))
            
            # Draw main text
            if offset == 0:
                screen.blit(text_surface, text_rect)
    
    def draw_neon_text(self, screen, text, x, y, size, color, pulse_offset=0):
        """Draw neon-style text with glow effect"""
        pulse = abs(math.sin(self.subtitle_pulse + pulse_offset)) * 0.2 + 0.8
        
        font = pygame.font.Font(None, size)
        
        # Draw glow layers
        glow_colors = [
            (*color, 30),   # Outer glow
            (*color, 60),   # Middle glow
            (*color, 120),  # Inner glow
            color           # Core text
        ]
        
        glow_sizes = [8, 6, 4, 0]
        
        for glow_color, glow_size in zip(glow_colors, glow_sizes):
            text_surface = font.render(text, True, glow_color[:3])
            text_rect = text_surface.get_rect(center=(x, y))
            
            if glow_size > 0:
                # Create glow effect
                glow_surf = pygame.Surface((text_surface.get_width() + glow_size * 2, 
                                          text_surface.get_height() + glow_size * 2), pygame.SRCALPHA)
                
                # Draw multiple copies for glow
                for dx in range(-glow_size, glow_size + 1, 2):
                    for dy in range(-glow_size, glow_size + 1, 2):
                        alpha = max(0, glow_color[3] - abs(dx) - abs(dy)) if len(glow_color) > 3 else 255
                        temp_surf = text_surface.copy()
                        temp_surf.set_alpha(alpha * pulse)
                        glow_surf.blit(temp_surf, (glow_size + dx, glow_size + dy))
                
                screen.blit(glow_surf, (text_rect.x - glow_size, text_rect.y - glow_size))
            else:
                # Main text
                text_surface.set_alpha(int(255 * pulse))
                screen.blit(text_surface, text_rect)
    
    def draw_simple_text(self, screen, text, x, y, size, color):
        """Draw simple, readable text with subtle background for better readability"""
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        
        # Draw subtle dark background for better readability
        bg_rect = text_rect.inflate(20, 10)  # Add padding
        bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 120))  # Semi-transparent black
        screen.blit(bg_surface, bg_rect)
        
        # Draw the text
        screen.blit(text_surface, text_rect)
    
    def draw(self, screen):
        """Draw the home screen"""
        # Dark background
        screen.fill((5, 5, 15))
        
        # Draw animated background
        self.animated_background.draw(screen)
        
        # Draw main title "Q-BERT" in graffiti style
        title_colors = [
            (255, 0, 255),    # Magenta outer glow
            (255, 100, 255),  # Pink middle glow
            (255, 200, 255),  # Light pink inner glow
            (255, 255, 255),  # White core
        ]
        
        self.draw_graffiti_text(screen, "Q-BERT", self.width // 2, self.height // 2 - 100, 
                               120, title_colors)
        
        # Draw subtitle "CREATED BY CLOUD KING" in simple, readable text
        self.draw_simple_text(screen, "CREATED BY CLOUD KING", 
                             self.width // 2, self.height // 2 - 20, 
                             32, NEON_CYAN)
        
        # Draw instructions in simple, readable text with pulsing color
        instruction_pulse = abs(math.sin(self.instruction_pulse)) * 0.5 + 0.5
        instruction_color = tuple(int(c * instruction_pulse) for c in NEON_GREEN)
        
        self.draw_simple_text(screen, "PRESS 'S' TO START", 
                             self.width // 2, self.height // 2 + 80, 
                             40, instruction_color)
        
        # Draw additional retro elements
        self.draw_retro_elements(screen)
    
    def draw_retro_elements(self, screen):
        """Draw additional 80s retro elements"""
        # Draw corner decorations
        corner_size = 50
        
        # Top corners
        pygame.draw.lines(screen, NEON_PURPLE, False, [
            (20, 20), (20 + corner_size, 20), (20 + corner_size, 20 + corner_size)
        ], 3)
        
        pygame.draw.lines(screen, NEON_PURPLE, False, [
            (self.width - 20, 20), (self.width - 20 - corner_size, 20), 
            (self.width - 20 - corner_size, 20 + corner_size)
        ], 3)
        
        # Bottom corners
        pygame.draw.lines(screen, NEON_PURPLE, False, [
            (20, self.height - 20), (20 + corner_size, self.height - 20), 
            (20 + corner_size, self.height - 20 - corner_size)
        ], 3)
        
        pygame.draw.lines(screen, NEON_PURPLE, False, [
            (self.width - 20, self.height - 20), (self.width - 20 - corner_size, self.height - 20), 
            (self.width - 20 - corner_size, self.height - 20 - corner_size)
        ], 3)
        
        # Draw scan lines effect
        for y in range(0, self.height, 4):
            alpha = 20 + 10 * abs(math.sin(y * 0.1 + self.title_pulse))
            line_surf = pygame.Surface((self.width, 1), pygame.SRCALPHA)
            line_surf.fill((0, 255, 255, int(alpha)))
            screen.blit(line_surf, (0, y))

class HighScoreEntry:
    def __init__(self, width, height, score, level):
        self.width = width
        self.height = height
        self.score = score
        self.level = level
        self.player_name = ""
        self.max_name_length = 12
        self.cursor_blink = 0
        self.entry_complete = False
        self.choice = None  # "continue" or "home"
        self.animated_background = AnimatedBackground(width, height)
        
    def update(self):
        """Update high score entry screen"""
        self.animated_background.update()
        self.cursor_blink += 0.1
        
    def handle_input(self, event):
        """Handle keyboard input for name entry"""
        if event.type == pygame.KEYDOWN:
            if not self.entry_complete:
                # Name entry phase
                if event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    if len(self.player_name.strip()) > 0:
                        self.entry_complete = True
                elif event.unicode.isprintable() and len(self.player_name) < self.max_name_length:
                    self.player_name += event.unicode.upper()
            else:
                # Choice phase
                if event.key == pygame.K_c:
                    self.choice = "continue"
                elif event.key == pygame.K_h:
                    self.choice = "home"
    
    def draw(self, screen):
        """Draw the high score entry screen"""
        # Dark background
        screen.fill((5, 5, 15))
        
        # Draw animated background
        self.animated_background.draw(screen)
        
        # Fonts
        title_font = pygame.font.Font(None, 64)
        text_font = pygame.font.Font(None, 36)
        name_font = pygame.font.Font(None, 48)
        
        if not self.entry_complete:
            # Name entry phase
            # Title
            title_text = title_font.render("NEW HIGH SCORE!", True, NEON_PINK)
            title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 150))
            screen.blit(title_text, title_rect)
            
            # Score display
            score_text = text_font.render(f"Score: {self.score}", True, NEON_CYAN)
            score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2 - 100))
            screen.blit(score_text, score_rect)
            
            level_text = text_font.render(f"Level: {self.level}", True, NEON_CYAN)
            level_rect = level_text.get_rect(center=(self.width // 2, self.height // 2 - 70))
            screen.blit(level_text, level_rect)
            
            # Name entry prompt
            prompt_text = text_font.render("Enter your name:", True, WHITE)
            prompt_rect = prompt_text.get_rect(center=(self.width // 2, self.height // 2 - 20))
            screen.blit(prompt_text, prompt_rect)
            
            # Name input box with background
            name_box_rect = pygame.Rect(self.width // 2 - 150, self.height // 2 + 20, 300, 50)
            pygame.draw.rect(screen, (20, 20, 40), name_box_rect)
            pygame.draw.rect(screen, NEON_CYAN, name_box_rect, 3)
            
            # Player name text
            display_name = self.player_name
            if abs(math.sin(self.cursor_blink)) > 0.5:  # Blinking cursor
                display_name += "_"
            
            name_text = name_font.render(display_name, True, WHITE)
            name_rect = name_text.get_rect(center=name_box_rect.center)
            screen.blit(name_text, name_rect)
            
            # Instructions
            instruction_text = text_font.render("Press ENTER when done", True, NEON_GREEN)
            instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height // 2 + 100))
            screen.blit(instruction_text, instruction_rect)
            
        else:
            # Choice phase
            # Confirmation
            confirm_text = title_font.render("Score Saved!", True, NEON_GREEN)
            confirm_rect = confirm_text.get_rect(center=(self.width // 2, self.height // 2 - 100))
            screen.blit(confirm_text, confirm_rect)
            
            # Player name display
            name_display = text_font.render(f"Welcome, {self.player_name}!", True, NEON_CYAN)
            name_rect = name_display.get_rect(center=(self.width // 2, self.height // 2 - 50))
            screen.blit(name_display, name_rect)
            
            # Options
            continue_text = text_font.render("Press 'C' to Continue Playing", True, NEON_GREEN)
            continue_rect = continue_text.get_rect(center=(self.width // 2, self.height // 2 + 20))
            screen.blit(continue_text, continue_rect)
            
            home_text = text_font.render("Press 'H' for Home Screen", True, NEON_PINK)
            home_rect = home_text.get_rect(center=(self.width // 2, self.height // 2 + 60))
            screen.blit(home_text, home_rect)

class QBert:
    def __init__(self, start_row, start_col, sound_generator):
        self.row = start_row
        self.col = start_col
        self.size = 22  # Slightly larger for detailed sprite
        self.color = NEON_ORANGE  # Bright neon orange
        self.x = 0
        self.y = 0
        self.last_move_time = 0
        self.move_delay = 400  # Milliseconds between moves (increased for hop animation)
        self.sound_generator = sound_generator
        
        # Animation properties
        self.is_hopping = False
        self.hop_start_time = 0
        self.hop_duration = 300  # Duration of hop animation in ms
        self.start_x = 0
        self.start_y = 0
        self.target_x = 0
        self.target_y = 0
        self.hop_height = 40  # How high Q-Bert hops
        
        # Power-up effects
        self.active_powers = {}
        self.shield_active = False
        self.speed_boost_active = False
        self.original_move_delay = self.move_delay
        
        # Visual effects
        self.last_trail_time = 0
        self.trail_interval = 50  # Add trail every 50ms when moving
        
        # Falling off board
        self.is_falling = False
        self.fall_start_time = 0
        self.fall_duration = 1000  # 1 second fall animation
        self.fall_start_y = 0
        
        # Flying disc transport
        self.on_flying_disc = False
        self.flying_disc = None
        
    def apply_power_up(self, power_type):
        """Apply a power-up effect to Q-Bert"""
        current_time = pygame.time.get_ticks()
        
        if power_type == 'freeze':
            self.active_powers['freeze'] = current_time + 3000  # 3 seconds
            
        elif power_type == 'speed':
            self.active_powers['speed'] = current_time + 5000  # 5 seconds
            self.move_delay = self.original_move_delay // 2  # Double speed
            self.speed_boost_active = True
            
        elif power_type == 'shield':
            self.active_powers['shield'] = current_time + 10000  # 10 seconds
            self.shield_active = True
            
        elif power_type == 'disc':
            # Flying disc - teleport to safety (top of pyramid)
            return 'teleport'
            
        elif power_type == 'bomb':
            # Color bomb - change nearby cubes
            return 'color_bomb'
            
        return None
    
    def update_power_effects(self):
        """Update active power-up effects"""
        current_time = pygame.time.get_ticks()
        
        # Check expired power-ups
        expired_powers = []
        for power, end_time in self.active_powers.items():
            if current_time > end_time:
                expired_powers.append(power)
        
        # Remove expired power-ups
        for power in expired_powers:
            del self.active_powers[power]
            
            if power == 'speed':
                self.move_delay = self.original_move_delay
                self.speed_boost_active = False
            elif power == 'shield':
                self.shield_active = False
    
    def is_freeze_active(self):
        """Check if freeze power is active"""
        return 'freeze' in self.active_powers
        
    def update_position(self, pyramid):
        """Update Q-Bert's screen position based on current cube"""
        if self.row < len(pyramid) and self.col < len(pyramid[self.row]):
            cube = pyramid[self.row][self.col]
            self.x = cube.x
            self.y = cube.y - 40  # Position Q-Bert above the larger cube
    
    def update(self):
        """Update Q-Bert's animation state and power effects"""
        # Update power-up effects
        self.update_power_effects()
        
        # Handle falling animation
        if self.is_falling:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.fall_start_time
            
            if elapsed >= self.fall_duration:
                # Fall complete
                self.is_falling = False
                return "fall_complete"
            else:
                # Animate falling (accelerating downward)
                progress = elapsed / self.fall_duration
                fall_distance = 200 * progress * progress  # Quadratic fall
                self.y = self.fall_start_y + fall_distance
                
                # Add rotation effect while falling
                rotation_angle = progress * 4 * math.pi  # 2 full rotations
        
        # Handle normal hopping animation
        elif self.is_hopping:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.hop_start_time
            
            if elapsed >= self.hop_duration:
                # Hop finished
                self.is_hopping = False
                self.x = self.target_x
                self.y = self.target_y
            else:
                # Calculate hop position
                progress = elapsed / self.hop_duration
                
                # Linear interpolation for x and y
                self.x = self.start_x + (self.target_x - self.start_x) * progress
                base_y = self.start_y + (self.target_y - self.start_y) * progress
                
                # Add parabolic hop height (peaks at middle of hop)
                hop_progress = 4 * progress * (1 - progress)  # Parabolic curve
                self.y = base_y - (self.hop_height * hop_progress)
        
        return None
    
    def start_hop(self, target_x, target_y):
        """Start a hop animation to target position"""
        self.is_hopping = True
        self.hop_start_time = pygame.time.get_ticks()
        self.start_x = self.x
        self.start_y = self.y
        self.target_x = target_x
        self.target_y = target_y
        
        # Play hop sound if available
        hop_sound = self.sound_generator.generate_hop_sound()
        if hop_sound:
            hop_sound.play()
    
    def move(self, direction, pyramid, particle_system=None, screen_shake=None):
        """Move Q-Bert in the specified direction with hopping animation"""
        # Don't allow movement if already hopping, falling, or on flying disc
        if self.is_hopping or self.is_falling or self.on_flying_disc:
            return False
            
        new_row, new_col = self.row, self.col
        
        if direction == "down_left":
            new_row += 1
            new_col = self.col
        elif direction == "down_right":
            new_row += 1
            new_col = self.col + 1
        elif direction == "up_left":
            new_row -= 1
            new_col = self.col - 1
        elif direction == "up_right":
            new_row -= 1
            new_col = self.col
        
        # Check if the new position is valid
        if (0 <= new_row < len(pyramid) and 
            0 <= new_col < len(pyramid[new_row])):
            
            # Calculate target position
            target_cube = pyramid[new_row][new_col]
            target_x = target_cube.x
            target_y = target_cube.y - 40  # Updated for larger cubes
            
            # Start hop animation
            self.start_hop(target_x, target_y)
            
            # Update logical position
            self.row = new_row
            self.col = new_col
            
            # Step on the cube with effects
            return pyramid[self.row][self.col].step_on(particle_system, screen_shake)
        else:
            # Q-Bert fell off the pyramid - start falling animation
            self.start_falling()
            return "fell_off"
    
    def start_falling(self):
        """Start the falling off animation"""
        self.is_falling = True
        self.fall_start_time = pygame.time.get_ticks()
        self.fall_start_y = self.y
    
    def board_to_flying_disc(self, flying_disc):
        """Transport Q-Bert to flying disc"""
        self.on_flying_disc = True
        self.flying_disc = flying_disc
        self.is_hopping = False
        self.is_falling = False
    
    def draw(self, screen, particle_system):
        """Draw Q-Bert with authentic 80s arcade sprite design"""
        # Add movement trails when hopping
        current_time = pygame.time.get_ticks()
        if self.is_hopping and current_time - self.last_trail_time > self.trail_interval:
            particle_system.add_trail(self.x, self.y, self.color, 3)
            self.last_trail_time = current_time
        
        # Add falling trail effects
        if self.is_falling:
            particle_system.add_trail(self.x, self.y, (255, 255, 0), 5)  # Yellow trail when falling
        
        # Draw shield effect if active
        if self.shield_active:
            shield_size = self.size + 15
            shield_surf = pygame.Surface((shield_size * 2, shield_size * 2), pygame.SRCALPHA)
            shield_alpha = int(120 + 60 * abs(math.sin(pygame.time.get_ticks() * 0.01)))
            pygame.draw.circle(shield_surf, (0, 255, 0, shield_alpha), 
                             (shield_size, shield_size), shield_size, 4)
            screen.blit(shield_surf, (int(self.x - shield_size), int(self.y - shield_size)))
        
        # Draw speed boost effect if active
        if self.speed_boost_active:
            for i in range(4):
                trail_size = self.size - i * 4
                trail_alpha = 180 - i * 45
                if trail_size > 0:
                    trail_surf = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                    pygame.draw.circle(trail_surf, (255, 255, 0, trail_alpha), 
                                     (trail_size, trail_size), trail_size)
                    screen.blit(trail_surf, (int(self.x - trail_size), int(self.y - trail_size)))
        
        # Authentic Q-Bert body (orange/yellow gradient like original)
        body_size = self.size
        
        # Main body - orange with authentic 80s coloring
        main_color = (255, 165, 0)  # Classic Q-Bert orange
        pygame.draw.circle(screen, main_color, (int(self.x), int(self.y)), body_size)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), body_size, 2)
        
        # Q-Bert's distinctive trunk/snout (more prominent like original)
        trunk_length = 12
        trunk_width = 8
        trunk_points = [
            (int(self.x - trunk_width//2), int(self.y + 8)),
            (int(self.x + trunk_width//2), int(self.y + 8)),
            (int(self.x + trunk_width//3), int(self.y + trunk_length + 8)),
            (int(self.x - trunk_width//3), int(self.y + trunk_length + 8))
        ]
        pygame.draw.polygon(screen, (255, 200, 100), trunk_points)  # Lighter orange for trunk
        pygame.draw.polygon(screen, BLACK, trunk_points, 2)
        
        # Large cartoon eyes (authentic 80s style - bigger and more expressive)
        eye_size = 8
        eye_offset_x = 10
        eye_offset_y = -8
        
        # Left eye (white with black pupil)
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x - eye_offset_x), int(self.y + eye_offset_y)), eye_size)
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x - eye_offset_x), int(self.y + eye_offset_y)), eye_size, 2)
        # Large black pupil (more cartoon-like)
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x - eye_offset_x + 2), int(self.y + eye_offset_y + 2)), 4)
        # Small white highlight
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x - eye_offset_x + 3), int(self.y + eye_offset_y + 1)), 2)
        
        # Right eye (white with black pupil)
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x + eye_offset_x), int(self.y + eye_offset_y)), eye_size)
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x + eye_offset_x), int(self.y + eye_offset_y)), eye_size, 2)
        # Large black pupil
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x + eye_offset_x - 2), int(self.y + eye_offset_y + 2)), 4)
        # Small white highlight
        pygame.draw.circle(screen, WHITE, 
                         (int(self.x + eye_offset_x - 3), int(self.y + eye_offset_y + 1)), 2)
        
        # Q-Bert's legs/feet (simple orange circles like original)
        foot_size = 6
        foot_y = int(self.y + body_size - 2)
        
        # Left foot
        pygame.draw.circle(screen, main_color, 
                         (int(self.x - 12), foot_y), foot_size)
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x - 12), foot_y), foot_size, 2)
        
        # Right foot
        pygame.draw.circle(screen, main_color, 
                         (int(self.x + 12), foot_y), foot_size)
        pygame.draw.circle(screen, BLACK, 
                         (int(self.x + 12), foot_y), foot_size, 2)
        
        # Add Q-Bert's signature "spring" coils when hopping (like original)
        if self.is_hopping:
            spring_color = (200, 200, 200)  # Light gray springs
            # Left spring
            spring_points_left = [
                (int(self.x - 8), int(self.y + body_size)),
                (int(self.x - 10), int(self.y + body_size + 5)),
                (int(self.x - 6), int(self.y + body_size + 10)),
                (int(self.x - 12), int(self.y + body_size + 15))
            ]
            for i in range(len(spring_points_left) - 1):
                pygame.draw.line(screen, spring_color, spring_points_left[i], spring_points_left[i+1], 2)
            
            # Right spring
            spring_points_right = [
                (int(self.x + 8), int(self.y + body_size)),
                (int(self.x + 10), int(self.y + body_size + 5)),
                (int(self.x + 6), int(self.y + body_size + 10)),
                (int(self.x + 12), int(self.y + body_size + 15))
            ]
            for i in range(len(spring_points_right) - 1):
                pygame.draw.line(screen, spring_color, spring_points_right[i], spring_points_right[i+1], 2)
        
        # Add rotation effect when falling (spinning Q-Bert)
        if self.is_falling:
            # Draw motion blur lines around Q-Bert
            for i in range(8):
                angle = i * math.pi / 4 + (pygame.time.get_ticks() * 0.02)
                start_x = self.x + math.cos(angle) * (body_size + 8)
                start_y = self.y + math.sin(angle) * (body_size + 8)
                end_x = self.x + math.cos(angle) * (body_size + 15)
                end_y = self.y + math.sin(angle) * (body_size + 15)
                pygame.draw.line(screen, (255, 255, 0, 150), 
                               (int(start_x), int(start_y)), (int(end_x), int(end_y)), 2)

class Game:
    def __init__(self):
        # Game state
        self.game_state = "home"  # "home", "playing", or "high_score_entry"
        self.home_screen = HomeScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.high_score_entry = None
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Q-Bert - Retro Arcade Experience")
        self.clock = pygame.time.Clock()
        self.sound_generator = SoundGenerator()
        self.score = 0
        self.level = 1  # Initialize level before creating pyramid
        self.lives = 3
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_delay = 3000  # 3 seconds between enemy spawns
        self.game_over = False
        
        # Power-up system
        self.power_ups = []
        self.power_spawn_timer = 0
        self.power_spawn_delay = 10000  # 10 seconds between power-up spawns
        
        # Advanced level features
        self.moving_platforms = []
        self.teleporter_pairs = []
        self.is_bonus_round = False
        
        # Visual effects systems
        self.particle_system = ParticleSystem()
        self.screen_shake = ScreenShake()
        self.animated_background = AnimatedBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Audio system
        self.audio_manager = AudioManager(self.sound_generator)
        
        # Progression system
        self.progression_system = ProgressionSystem()
        self.game_start_time = pygame.time.get_ticks()
        self.level_start_time = pygame.time.get_ticks()
        self.level_perfect = True  # Track if current level is perfect
        self.newly_unlocked_achievements = []
        
        # Create pyramid after level is set
        self.pyramid = self.create_pyramid()
        self.qbert = QBert(0, 0, self.sound_generator)  # Start at top of pyramid
        self.qbert.update_position(self.pyramid)
        
        # Start background music and ambient sounds
        self.audio_manager.play_background_music(self.level)
        self.audio_manager.play_ambient_atmosphere()
        
        # Update statistics
        self.progression_system.update_statistics(games_played=1)
        
        # Initialize game components (only when starting to play)
        self.pyramid = None
        self.qbert = None
    
    def start_game(self):
        """Initialize game components when starting to play"""
        print("Initializing game components...")  # Debug message
        self.game_state = "playing"
        
        # Reset game state
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_over = False
        self.enemies.clear()
        self.power_ups.clear()
        self.enemy_spawn_timer = pygame.time.get_ticks()
        self.power_spawn_timer = pygame.time.get_ticks()
        self.game_start_time = pygame.time.get_ticks()
        self.level_start_time = pygame.time.get_ticks()
        self.level_perfect = True
        
        # Create pyramid after level is set
        self.pyramid = self.create_pyramid()
        self.qbert = QBert(0, 0, self.sound_generator)  # Start at top of pyramid
        self.qbert.update_position(self.pyramid)
        
        # Start background music and ambient sounds
        if hasattr(self, 'audio_manager'):
            self.audio_manager.play_background_music(self.level)
            self.audio_manager.play_ambient_atmosphere()
        
        print("Game started successfully!")  # Debug message
        
    def create_pyramid(self):
        """Create the pyramid of cubes with tighter spacing for connected look"""
        pyramid = []
        pyramid_size = 7  # 7 rows
        start_x = SCREEN_WIDTH // 2
        start_y = 120  # Moved up slightly
        
        # Clear advanced features for new level
        self.moving_platforms.clear()
        self.teleporter_pairs.clear()
        
        for row in range(pyramid_size):
            cube_row = []
            cubes_in_row = row + 1
            
            for col in range(cubes_in_row):
                # Tighter spacing for connected appearance
                x = start_x + (col - row/2) * 60  # Increased spacing for larger cubes
                y = start_y + row * 40  # Adjusted vertical spacing
                
                # Level 6+: Some cubes become moving platforms
                if self.level >= 6 and row > 1 and row < 5:  # Middle rows only
                    import random
                    if random.random() < 0.3:  # 30% chance
                        moving_platform = MovingPlatform(row, col, x, y, self.sound_generator, self.level)
                        self.moving_platforms.append(moving_platform)
                        cube_row.append(moving_platform.cube)
                        continue
                
                cube = Cube(row, col, x, y, self.sound_generator, self.level, self.progression_system)
                
                # Level 9+: Some cubes become teleporters
                if self.level >= 9 and row > 0 and row < 6:  # Not top or bottom
                    import random
                    if random.random() < 0.2:  # 20% chance
                        cube.is_teleporter = True
                        cube.teleporter_id = len(self.teleporter_pairs)
                        # Find or create teleporter pair
                        if len(self.teleporter_pairs) == 0 or len(self.teleporter_pairs[-1]) == 2:
                            self.teleporter_pairs.append([cube])
                        else:
                            self.teleporter_pairs[-1].append(cube)
                
                cube_row.append(cube)
            
            pyramid.append(cube_row)
        
        return pyramid
    
    def update_pyramid_colors(self):
        """Update all cube colors for the current level"""
        for row in self.pyramid:
            for cube in row:
                cube.update_color_scheme(self.level, self.progression_system)
    
    def spawn_power_up(self):
        """Spawn a random power-up on the pyramid"""
        current_time = pygame.time.get_ticks()
        if current_time - self.power_spawn_timer > self.power_spawn_delay:
            # Choose random power-up type
            import random
            power_types = ['freeze', 'speed', 'shield', 'disc', 'bomb']
            power_type = random.choice(power_types)
            
            # Choose random position on pyramid (not top cube where Q-Bert starts)
            available_positions = []
            for row_idx, row in enumerate(self.pyramid):
                for col_idx, cube in enumerate(row):
                    if not (row_idx == 0 and col_idx == 0):  # Not starting position
                        available_positions.append((row_idx, col_idx, cube))
            
            if available_positions:
                row_idx, col_idx, cube = random.choice(available_positions)
                power_up = PowerUp(row_idx, col_idx, cube.x, cube.y - 20, power_type, self.sound_generator)
                self.power_ups.append(power_up)
                self.power_spawn_timer = current_time
    
    def check_power_up_collection(self):
        """Check if Q-Bert collected any power-ups"""
        for power_up in self.power_ups[:]:
            if (power_up.row == self.qbert.row and 
                power_up.col == self.qbert.col and 
                not power_up.collected):
                
                # Collect power-up
                power_up.collected = True
                result = self.qbert.apply_power_up(power_up.power_type)
                
                # Track power-up collection
                self.progression_system.update_statistics(power_ups_collected=1)
                
                # Play power-up sound
                self.audio_manager.play_power_up_sound()
                
                # Handle special power-up effects
                if result == 'teleport':
                    # Flying disc - teleport to top
                    self.qbert.row = 0
                    self.qbert.col = 0
                    self.qbert.update_position(self.pyramid)
                elif result == 'color_bomb':
                    # Color bomb - change nearby cubes
                    self.activate_color_bomb(self.qbert.row, self.qbert.col)
                
                # Add score bonus
                self.score += 100
                
                # Remove collected power-up
                self.power_ups.remove(power_up)
                break
    
    def end_game(self):
        """Handle game over - check for high score and update statistics"""
        # Calculate total playtime
        total_time = (pygame.time.get_ticks() - self.game_start_time) / 1000.0
        
        # Update final statistics
        self.progression_system.update_statistics(total_playtime=total_time)
        
        # Check if this is a high score (top 10)
        high_scores = self.progression_system.get_high_scores()
        is_high_score = len(high_scores) < 10 or self.score > high_scores[-1]['score']
        
        if is_high_score:
            # Enter high score entry mode
            self.game_state = "high_score_entry"
            self.high_score_entry = HighScoreEntry(SCREEN_WIDTH, SCREEN_HEIGHT, self.score, self.level)
        else:
            # Add score without name entry
            self.progression_system.add_high_score(self.score, self.level)
        
        # Check for final achievements
        self.newly_unlocked_achievements.extend(self.progression_system.check_achievements())
    
    def activate_color_bomb(self, center_row, center_col):
        """Activate color bomb effect - change nearby cubes"""
        # Add dramatic screen shake for color bomb
        self.screen_shake.add_shake(20, 8)
        
        # Change cubes in a 3x3 area around Q-Bert
        for row_offset in range(-1, 2):
            for col_offset in range(-1, 2):
                target_row = center_row + row_offset
                target_col = center_col + col_offset
                
                if (0 <= target_row < len(self.pyramid) and 
                    0 <= target_col < len(self.pyramid[target_row])):
                    cube = self.pyramid[target_row][target_col]
                    if cube.step_on(self.particle_system, self.screen_shake):  # Pass effects
                        self.score += 25
                        # Add extra explosion particles for color bomb
                        self.particle_system.add_explosion(cube.x, cube.y - 15, NEON_ORANGE, 20)
    
    def update_power_ups(self):
        """Update all power-ups"""
        for power_up in self.power_ups[:]:
            if not power_up.update():
                self.power_ups.remove(power_up)
    
    def spawn_enemy(self):
        """Spawn a new enemy at the top of the pyramid"""
        # Check if there's already a Coily on the board
        coily_exists = any(isinstance(enemy, Coily) for enemy in self.enemies)
        
        if coily_exists:
            return  # Don't spawn another Coily if one already exists
        
        current_time = pygame.time.get_ticks()
        if current_time - self.enemy_spawn_timer > self.enemy_spawn_delay:
            # Only spawn Coily, with current level for speed scaling
            enemy = Coily(self.sound_generator, self.level)
            
            # Start at top of pyramid
            enemy.row = 0
            enemy.col = 0
            enemy.update_position(self.pyramid)
            
            self.enemies.append(enemy)
            self.enemy_spawn_timer = current_time
            
            # Play enemy spawn sound
            self.audio_manager.play_enemy_sound("coily")
    
    def check_collisions(self):
        """Check for collisions between Q-Bert and enemies"""
        for enemy in self.enemies[:]:  # Use slice to avoid modification during iteration
            # Check if Q-Bert and enemy are on the same cube
            if (self.qbert.row == enemy.row and 
                self.qbert.col == enemy.col and 
                not self.qbert.is_hopping and 
                not enemy.is_hopping):
                
                # Check if Q-Bert has shield protection
                if self.qbert.shield_active:
                    # Shield protects - remove enemy instead
                    self.enemies.remove(enemy)
                    self.score += 50  # Bonus for shield kill
                    # Track enemy defeat
                    self.progression_system.update_statistics(enemies_defeated=1)
                    # Deactivate shield after use
                    if 'shield' in self.qbert.active_powers:
                        del self.qbert.active_powers['shield']
                    self.qbert.shield_active = False
                else:
                    # Q-Bert caught by enemy!
                    self.lives -= 1
                    self.level_perfect = False  # Level is no longer perfect
                    self.reset_positions()
                    
                    if self.lives <= 0:
                        self.game_over = True
                        self.end_game()
                
                break
    
    def reset_positions(self):
        """Reset Q-Bert and clear enemies after being caught"""
        self.qbert = QBert(0, 0, self.sound_generator)
        self.qbert.update_position(self.pyramid)
        self.enemies.clear()
        self.power_ups.clear()  # Clear power-ups on reset
        self.enemy_spawn_timer = pygame.time.get_ticks()
        self.power_spawn_timer = pygame.time.get_ticks()
    
    def update_enemies(self):
        """Update all enemy positions and AI"""
        for enemy in self.enemies[:]:
            # Update enemy animation first
            enemy_result = enemy.update()
            if enemy_result == "fall_complete":
                # Enemy fell off - remove it and award points
                self.enemies.remove(enemy)
                self.score += 25
                self.progression_system.update_statistics(enemies_defeated=1)
                continue
            
            # Move enemy based on AI (pass freeze status)
            if hasattr(enemy, 'ai_move') and not enemy.is_falling:
                ai_result = enemy.ai_move(self.qbert.row, self.qbert.col, self.pyramid, 
                                        self.qbert.is_freeze_active())
                
                if ai_result == "fell_off":
                    # Enemy will start falling animation
                    pass
            
            # Remove enemies that are completely off screen or invalid positions
            if (enemy.row >= len(self.pyramid) or 
                (enemy.row >= 0 and enemy.col >= len(self.pyramid[enemy.row])) or
                enemy.row < 0 or enemy.col < 0) and not enemy.is_falling:
                # Only remove if not already falling (falling enemies are handled elsewhere)
                self.enemies.remove(enemy)
    
    def check_level_complete(self):
        """Check if all cubes are completed (multi-step aware)"""
        for row in self.pyramid:
            for cube in row:
                if not cube.is_complete:
                    return False
        return True
    
    def handle_input(self, event=None):
        """Handle keyboard input for Q-Bert movement"""
        # Don't allow input if Q-Bert doesn't exist or is currently hopping
        if self.qbert is None or self.qbert.is_hopping:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Only process movement if enough time has passed since last move
        if current_time - self.qbert.last_move_time < self.qbert.move_delay:
            return
        
        # Handle key press events (single press, not continuous)
        if event and event.type == pygame.KEYDOWN:
            moved = False
            
            if event.key == pygame.K_q:  # Q key - up-left
                result = self.qbert.move("up_left", self.pyramid, self.particle_system, self.screen_shake)
                moved = True
            elif event.key == pygame.K_w:  # W key - up-right
                result = self.qbert.move("up_right", self.pyramid, self.particle_system, self.screen_shake)
                moved = True
            elif event.key == pygame.K_a:  # A key - down-left
                result = self.qbert.move("down_left", self.pyramid, self.particle_system, self.screen_shake)
                moved = True
            elif event.key == pygame.K_s:  # S key - down-right
                result = self.qbert.move("down_right", self.pyramid, self.particle_system, self.screen_shake)
                moved = True
            
            if moved:
                self.qbert.last_move_time = current_time
                if result == True:
                    self.score += 25
    
    def draw(self):
        """Draw everything on screen with visual effects"""
        # Get screen shake offset
        shake_x, shake_y = self.screen_shake.get_offset()
        
        # Dark background with animated elements
        self.screen.fill((5, 5, 15))  # Very dark blue background
        
        # Draw animated background
        self.animated_background.draw(self.screen)
        
        # Create a surface for the main game content (for screen shake)
        game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Draw pyramid on game surface
        for row in self.pyramid:
            for cube in row:
                # Temporarily adjust cube position for screen shake
                original_x, original_y = cube.x, cube.y
                cube.x += shake_x
                cube.y += shake_y
                cube.draw(game_surface)
                cube.x, cube.y = original_x, original_y
        
        # Draw moving platforms on game surface
        for platform in self.moving_platforms:
            original_x, original_y = platform.x, platform.y
            platform.x += shake_x
            platform.y += shake_y
            platform.cube.x += shake_x
            platform.cube.y += shake_y
            platform.draw(game_surface)
            platform.x, platform.y = original_x, original_y
            platform.cube.x, platform.cube.y = original_x, original_y
        
        # Draw Q-Bert on game surface
        original_x, original_y = self.qbert.x, self.qbert.y
        self.qbert.x += shake_x
        self.qbert.y += shake_y
        self.qbert.draw(game_surface, self.particle_system)
        self.qbert.x, self.qbert.y = original_x, original_y
        
        # Draw enemies on game surface
        for enemy in self.enemies:
            original_x, original_y = enemy.x, enemy.y
            enemy.x += shake_x
            enemy.y += shake_y
            enemy.draw(game_surface, self.particle_system)
            enemy.x, enemy.y = original_x, original_y
        
        # Draw power-ups on game surface
        for power_up in self.power_ups:
            original_x, original_y = power_up.x, power_up.y
            power_up.x += shake_x
            power_up.y += shake_y
            power_up.draw(game_surface)
            power_up.x, power_up.y = original_x, original_y
        
        # Draw particles on game surface (they handle their own shake)
        self.particle_system.draw(game_surface)
        
        # Blit the game surface to the main screen
        self.screen.blit(game_surface, (0, 0))
        
        # Draw UI with neon colors
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, NEON_CYAN)
        level_text = font.render(f"Level: {self.level}", True, NEON_GREEN)
        lives_text = font.render(f"Lives: {self.lives}", True, HOT_PINK)
        
        # Add color theme indicator
        theme_font = pygame.font.Font(None, 24)
        available_themes = self.progression_system.get_available_themes()
        theme_index = (self.level - 1) % len(available_themes)
        current_theme_id = available_themes[theme_index]
        
        # Theme names including bonus themes
        theme_names = {
            1: "Cyan Storm", 2: "Hot Pink Fury", 3: "Acid Green Rush",
            4: "Purple Lightning", 5: "Laser Red Heat", 6: "Electric Blue Wave",
            7: "Lightning", 8: "Survivor", 9: "Warrior", 10: "Mystic",
            11: "Rainbow", 12: "Endurance", 13: "Legendary"
        }
        
        theme_name = theme_names.get(current_theme_id, f"Theme {current_theme_id}")
        color_scheme = get_color_scheme(self.level, self.progression_system)
        theme_text = theme_font.render(f"Theme: {theme_name}", True, color_scheme['target_top'])
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(level_text, (10, 50))
        self.screen.blit(lives_text, (10, 90))
        self.screen.blit(theme_text, (10, 130))
        
        # Show high score
        high_scores = self.progression_system.get_high_scores()
        if high_scores:
            high_score_text = theme_font.render(f"High Score: {high_scores[0]['score']}", True, NEON_PINK)
            self.screen.blit(high_score_text, (10, 160))
        
        # Draw active power-up status
        power_y = 190
        power_font = pygame.font.Font(None, 24)
        if self.qbert.active_powers:
            power_status_text = power_font.render("Active Powers:", True, WHITE)
            self.screen.blit(power_status_text, (10, power_y))
            power_y += 25
            
            current_time = pygame.time.get_ticks()
            for power, end_time in self.qbert.active_powers.items():
                remaining = max(0, (end_time - current_time) // 1000)
                power_text = power_font.render(f"{power.upper()}: {remaining}s", True, NEON_CYAN)
                self.screen.blit(power_text, (10, power_y))
                power_y += 20
        
        # Show achievement notifications
        if self.newly_unlocked_achievements:
            achievement_y = SCREEN_HEIGHT - 150
            achievement_font = pygame.font.Font(None, 28)
            
            for i, achievement in enumerate(self.newly_unlocked_achievements[-3:]):  # Show last 3
                achievement_text = achievement_font.render(f"🏆 {achievement['name']} Unlocked!", True, NEON_PINK)
                self.screen.blit(achievement_text, (10, achievement_y + i * 30))
        
        # Show statistics in corner
        stats = self.progression_system.get_statistics()
        stats_font = pygame.font.Font(None, 20)
        stats_y = SCREEN_HEIGHT - 80
        
        stats_text = [
            f"Hops: {stats.get('total_hops', 0)}",
            f"Enemies: {stats.get('enemies_defeated', 0)}",
            f"Power-ups: {stats.get('power_ups_collected', 0)}"
        ]
        
        for i, stat in enumerate(stats_text):
            text = stats_font.render(stat, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH - 120, stats_y + i * 20))
        
        # Draw controls with neon styling
        controls_font = pygame.font.Font(None, 24)
        controls = [
            "Controls:",
            "Q - Up-Left",
            "W - Up-Right", 
            "A - Down-Left",
            "S - Down-Right"
        ]
        
        # Add level feature info
        if self.level >= 3:
            controls.append("")
            controls.append("Multi-Step Cubes!")
        if self.level >= 6:
            controls.append("Moving Platforms!")
        if self.level >= 9:
            controls.append("Teleporter Cubes!")
        
        colors = [ELECTRIC_BLUE] + [WHITE] * (len(controls) - 1)
        for i, (control, color) in enumerate(zip(controls, colors)):
            text = controls_font.render(control, True, color)
            self.screen.blit(text, (SCREEN_WIDTH - 150, 10 + i * 25))
        
        # Draw game over screen with neon effects
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((5, 5, 15))  # Dark overlay
            self.screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.Font(None, 72)
            restart_font = pygame.font.Font(None, 36)
            small_font = pygame.font.Font(None, 24)
            
            game_over_text = game_over_font.render("GAME OVER", True, NEON_PINK)
            final_score_text = restart_font.render(f"Final Score: {self.score}", True, NEON_CYAN)
            final_level_text = restart_font.render(f"Level Reached: {self.level}", True, NEON_GREEN)
            restart_text = restart_font.render("Press R to Restart", True, NEON_GREEN)
            home_text = restart_font.render("Press H for Home Screen", True, NEON_CYAN)
            
            # Center the main text
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            level_rect = final_level_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            home_rect = home_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 90))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(final_score_text, score_rect)
            self.screen.blit(final_level_text, level_rect)
            self.screen.blit(restart_text, restart_rect)
            self.screen.blit(home_text, home_rect)
            
            # Show high scores
            high_scores = self.progression_system.get_high_scores()
            if high_scores:
                high_score_title = small_font.render("HIGH SCORES", True, NEON_PINK)
                self.screen.blit(high_score_title, (50, SCREEN_HEIGHT//2 + 100))
                
                for i, score_entry in enumerate(high_scores[:5]):  # Show top 5
                    score_text = small_font.render(
                        f"{i+1}. {score_entry['score']} (Level {score_entry['level']})", 
                        True, WHITE
                    )
                    self.screen.blit(score_text, (50, SCREEN_HEIGHT//2 + 130 + i * 20))
            
            # Show recent achievements
            achievements = self.progression_system.get_achievements()
            if achievements:
                achievement_title = small_font.render("ACHIEVEMENTS", True, NEON_PINK)
                self.screen.blit(achievement_title, (SCREEN_WIDTH - 250, SCREEN_HEIGHT//2 + 100))
                
                achievement_list = list(achievements.items())[-5:]  # Show last 5
                for i, (achievement_id, achievement_data) in enumerate(achievement_list):
                    achievement_def = self.progression_system.achievement_definitions.get(achievement_id, {})
                    achievement_text = small_font.render(
                        f"🏆 {achievement_def.get('name', achievement_id)}", 
                        True, NEON_CYAN
                    )
                    self.screen.blit(achievement_text, (SCREEN_WIDTH - 250, SCREEN_HEIGHT//2 + 130 + i * 20))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif self.game_state == "home":
                        if event.key == pygame.K_s:  # Start game
                            print("Starting game...")  # Debug message
                            self.start_game()
                    elif self.game_state == "high_score_entry":
                        if self.high_score_entry:
                            self.high_score_entry.handle_input(event)
                            if self.high_score_entry.choice == "continue":
                                # Save high score with name and continue
                                self.progression_system.add_high_score(
                                    self.score, self.level, self.high_score_entry.player_name.strip()
                                )
                                self.start_game()
                                self.high_score_entry = None
                            elif self.high_score_entry.choice == "home":
                                # Save high score with name and go home
                                self.progression_system.add_high_score(
                                    self.score, self.level, self.high_score_entry.player_name.strip()
                                )
                                self.game_state = "home"
                                self.high_score_entry = None
                                if hasattr(self, 'audio_manager'):
                                    self.audio_manager.stop_all_music()
                    elif self.game_state == "playing":
                        if not self.game_over:
                            # Pass the key event to handle_input
                            self.handle_input(event)
                        elif self.game_over and event.key == pygame.K_r:
                            # Restart game
                            self.start_game()
                        elif self.game_over and event.key == pygame.K_h:
                            # Return to home screen
                            self.game_state = "home"
                            if hasattr(self, 'audio_manager'):
                                self.audio_manager.stop_all_music()
                elif event.type == pygame.USEREVENT + 1:
                    # Resume background music after fanfare
                    if hasattr(self, 'audio_manager'):
                        self.audio_manager.resume_background_music()
                    pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Cancel timer
            
            # Update based on game state
            if self.game_state == "home":
                self.home_screen.update()
                self.home_screen.draw(self.screen)
            
            elif self.game_state == "high_score_entry":
                if self.high_score_entry:
                    self.high_score_entry.update()
                    self.high_score_entry.draw(self.screen)
            
            elif self.game_state == "playing" and self.qbert is not None:
                if not self.game_over:
                    # Update visual effects
                    self.particle_system.update()
                    self.screen_shake.update()
                    self.animated_background.update()
                    
                    # Update Q-Bert
                    qbert_result = self.qbert.update()
                
                if qbert_result == "fall_complete":
                    # Q-Bert fell off - lose life
                    self.lives -= 1
                    self.level_perfect = False
                    if self.lives <= 0:
                        self.game_over = True
                        self.end_game()
                    else:
                        self.reset_positions()
                
                # Update cube explosion effects and moving platforms
                for row in self.pyramid:
                    for cube in row:
                        cube.update()
                
                # Update moving platforms
                for platform in self.moving_platforms:
                    platform.update(self.pyramid)
                
                # Spawn and update power-ups
                self.spawn_power_up()
                self.update_power_ups()
                
                # Check power-up collection
                self.check_power_up_collection()
                
                # Spawn enemies
                self.spawn_enemy()
                
                # Update enemies with AI
                self.update_enemies()
                
                # Check collisions
                self.check_collisions()
                
                # Check for level completion
                if self.check_level_complete():
                    # Calculate level completion time
                    level_time = (pygame.time.get_ticks() - self.level_start_time) / 1000.0
                    
                    # Track level completion statistics
                    stats_update = {
                        "highest_level": self.level + 1,
                        "fastest_level": level_time
                    }
                    
                    if self.level_perfect:
                        stats_update["perfect_levels"] = 1
                    
                    self.progression_system.update_statistics(**stats_update)
                    
                    # Check for newly unlocked achievements
                    self.newly_unlocked_achievements = self.progression_system.check_achievements()
                    
                    # Play level complete fanfare
                    self.audio_manager.play_level_complete_fanfare()
                    
                    self.level += 1
                    self.pyramid = self.create_pyramid()  # Reset pyramid with new level colors
                    self.qbert = QBert(0, 0, self.sound_generator)  # Reset Q-Bert position
                    self.qbert.update_position(self.pyramid)
                    self.enemies.clear()  # Clear enemies for new level
                    self.power_ups.clear()  # Clear power-ups for new level
                    self.enemy_spawn_timer = pygame.time.get_ticks()
                    self.power_spawn_timer = pygame.time.get_ticks()
                    
                    # Reset level tracking
                    self.level_start_time = pygame.time.get_ticks()
                    self.level_perfect = True
                    
                    # Change background music for new level theme
                    if hasattr(self, 'audio_manager'):
                        self.audio_manager.play_background_music(self.level)
                
                # Draw game only when playing
                if self.game_state == "playing":
                    self.draw()
            
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
