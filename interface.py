from PyQt6.QtGui import QPainter,QColor
from PyQt6.QtWidgets import QMainWindow,QWidget
from PyQt6.QtCore import QSize, QTimer, QRect,QPoint,Qt
import config
import sound_player



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(QSize(config.window_width, config.window_height))
        self.setWindowTitle(config.window_title)
        self.main_widget = MainWidget(self)
        self.setCentralWidget(self.main_widget)

class MainWidget(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(config.tick_rate)


        self.game_over = False
        self.score = 0
        self.platform_move_left = False
        self.platform_move_right = False
        self.platform = QRect(int(config.window_width/2)-int(config.platform_width/2),config.window_height-config.platform_height-20, config.platform_width, config.platform_height)
        self.platform_velocity = config.platform_velocity
        self.ball = QPoint(int(config.window_width/2), int(config.window_height/2)+50)
        self.bricks = [QRect(i * config.brick_width,j *config.brick_height, config.brick_width, config.brick_height) for i in range(int(config.window_width/config.brick_width)) for j in range(int(config.window_height/2/config.brick_height))]
        self.ball_velocity = QPoint(config.ball_velocity_x,config.ball_velocity_y)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)


    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setBrush(QColor(*config.background_color))
        painter.drawRect(self.rect())

        painter.setBrush(QColor(*config.platform_color))
        painter.drawRect(self.platform)

        painter.setBrush(QColor(*config.ball_color))
        painter.drawEllipse(self.ball,config.ball_radius,config.ball_radius)

        painter.setBrush(QColor(*config.bricks_color))
        for brick in self.bricks:
            painter.drawRect(brick)

        if self.game_over:
            painter.setPen(QColor(*config.game_over_color))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"Game Over!\n Your score {self.score}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.platform_move_left = True
        elif event.key() == Qt.Key.Key_Right:
            self.platform_move_right = True
        elif event.key() == Qt.Key.Key_R:
            self.reset_game()
            sound_player.reset_sound.play()


    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.platform_move_left = False
        elif event.key() == Qt.Key.Key_Right:
            self.platform_move_right = False

    def update_game(self):
        if self.game_over:
            return

        if self.platform_move_left and self.platform_move_left and self.platform.left() > 0:
            self.platform.moveLeft(self.platform.left() - self.platform_velocity)
        if self.platform_move_right and self.platform_move_right and self.platform.right() < config.window_width:
            self.platform.moveLeft(self.platform.left() + self.platform_velocity)

        self.ball += self.ball_velocity

        if self.ball.y() <= 0+config.ball_radius:
            self.ball_velocity.setY(-self.ball_velocity.y())
            sound_player.hit_sound.play()

        if self.ball.x() <= 0+config.ball_radius:
            self.ball_velocity.setX(-self.ball_velocity.x())
            sound_player.hit_sound.play()
        elif self.ball.x() >= config.window_width-config.ball_radius:
            self.ball_velocity.setX(-self.ball_velocity.x())
            sound_player.hit_sound.play()

        if self.platform.contains(self.ball):
            self.ball_velocity.setY(-self.ball_velocity.y())
            sound_player.hit_sound.play()

        for brick in self.bricks:
            if brick.contains(self.ball):
                self.ball_velocity.setY(-self.ball_velocity.y())
                sound_player.brick_break_sound.play()
                self.bricks.remove(brick)
                self.score += 1
                break

        if self.ball.y() > config.window_height-config.ball_radius:
            sound_player.lose_sound.play()
            self.game_over = True

        if not self.bricks:
            sound_player.win_sound.play()
            self.reset_game()

        self.update()

    def reset_game(self):
        self.bricks.clear()
        self.platform.setRect(int(config.window_width / 2) - int(config.platform_width / 2),config.window_height - config.platform_height - 20, config.platform_width,config.platform_height)
        self.platform_velocity = config.platform_velocity
        self.ball.setX(int(config.window_width / 2))
        self.ball.setY(int(config.window_height / 2) + 50)
        self.bricks = [QRect(i * config.brick_width, j * config.brick_height, config.brick_width, config.brick_height) for i in range(int(config.window_width / config.brick_width)) for j in range(int(config.window_height / 2 / config.brick_height))]
        self.ball_velocity.setX(config.ball_velocity_x)
        self.ball_velocity.setY(config.ball_velocity_y)
        self.score = 0
        self.game_over = False



