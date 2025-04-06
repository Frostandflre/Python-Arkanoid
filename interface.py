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
    def __init__(self, parent):
        super().__init__(parent)

        # Таймер для запуска игрового цикла с заданной частотой
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(config.tick_rate)

        self.game_over = False
        self.score = 0

        # Флаги для управления движением платформы
        self.platform_move_left = False
        self.platform_move_right = False

        # Инициализация положения платформы (внизу по центру окна)
        self.platform = QRect(
            int(config.window_width / 2) - int(config.platform_width / 2),
            config.window_height - config.platform_height - 20,
            config.platform_width,
            config.platform_height
        )
        self.platform_velocity = config.platform_velocity

        # Начальная позиция мяча
        self.ball = QPoint(int(config.window_width / 2), int(config.window_height / 2) + 50)

        # Генерация всех кирпичей в виде сетки
        self.bricks = [
            QRect(i * config.brick_width, j * config.brick_height, config.brick_width, config.brick_height)
            for i in range(int(config.window_width / config.brick_width))
            for j in range(int(config.window_height / 2 / config.brick_height))
        ]

        # Начальная скорость мяча
        self.ball_velocity = QPoint(config.ball_velocity_x, config.ball_velocity_y)

        # Разрешение на обработку нажатий клавиш
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Отрисовка фона
        painter.setBrush(QColor(*config.background_color))
        painter.drawRect(self.rect())

        # Отрисовка платформы
        painter.setBrush(QColor(*config.platform_color))
        painter.drawRect(self.platform)

        # Отрисовка мяча
        painter.setBrush(QColor(*config.ball_color))
        painter.drawEllipse(self.ball, config.ball_radius, config.ball_radius)

        # Отрисовка кирпичей
        painter.setBrush(QColor(*config.bricks_color))
        for brick in self.bricks:
            painter.drawRect(brick)

        # Вывод текста окончания игры
        if self.game_over:
            painter.setPen(QColor(*config.game_over_color))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"Game Over!\n Your score {self.score}")

    def keyPressEvent(self, event):
        # Обработка нажатий клавиш для движения платформы и сброса игры
        if event.key() == Qt.Key.Key_Left:
            self.platform_move_left = True
        elif event.key() == Qt.Key.Key_Right:
            self.platform_move_right = True
        elif event.key() == Qt.Key.Key_R:
            self.reset_game()
            sound_player.reset_sound.play()

    def keyReleaseEvent(self, event):
        # Обработка отпускания клавиш
        if event.key() == Qt.Key.Key_Left:
            self.platform_move_left = False
        elif event.key() == Qt.Key.Key_Right:
            self.platform_move_right = False

    def update_game(self):
        # Если игра окончена — ничего не обновляем
        if self.game_over:
            return

        # Обработка движения платформы в пределах экрана
        if self.platform_move_left and self.platform.left() > 0:
            self.platform.moveLeft(self.platform.left() - self.platform_velocity)
        if self.platform_move_right and self.platform.right() < config.window_width:
            self.platform.moveLeft(self.platform.left() + self.platform_velocity)

        # Обновление положения мяча
        self.ball += self.ball_velocity

        # Отскок мяча от верхней границы
        if self.ball.y() <= config.ball_radius:
            self.ball_velocity.setY(-self.ball_velocity.y())
            sound_player.hit_sound.play()

        # Отскок мяча от боковых границ
        if self.ball.x() <= config.ball_radius or self.ball.x() >= config.window_width - config.ball_radius:
            self.ball_velocity.setX(-self.ball_velocity.x())
            sound_player.hit_sound.play()

        # Проверка столкновения мяча с платформой
        if self.platform.contains(self.ball):
            self.ball_velocity.setY(-self.ball_velocity.y())
            sound_player.hit_sound.play()

        # Проверка столкновения с кирпичами
        for brick in self.bricks:
            if brick.contains(self.ball):
                self.ball_velocity.setY(-self.ball_velocity.y())
                sound_player.brick_break_sound.play()
                self.bricks.remove(brick)
                self.score += 1
                break  # Выход из цикла, чтобы избежать ошибок при одновременном удалении нескольких кирпичей

        # Проверка на проигрыш (мяч ниже экрана)
        if self.ball.y() > config.window_height - config.ball_radius:
            sound_player.lose_sound.play()
            self.game_over = True

        # Проверка на победу (все кирпичи разрушены)
        if not self.bricks:
            sound_player.win_sound.play()
            self.reset_game()

        # Перерисовка экрана
        self.update()

    def reset_game(self):
        # Полный сброс всех параметров игры до начальных значений
        self.bricks.clear()
        self.platform.setRect(
            int(config.window_width / 2) - int(config.platform_width / 2),
            config.window_height - config.platform_height - 20,
            config.platform_width,
            config.platform_height
        )
        self.ball.setX(int(config.window_width / 2))
        self.ball.setY(int(config.window_height / 2) + 50)
        self.ball_velocity.setX(config.ball_velocity_x)
        self.ball_velocity.setY(config.ball_velocity_y)
        self.score = 0
        self.game_over = False

        # Повторное создание кирпичей
        self.bricks = [
            QRect(i * config.brick_width, j * config.brick_height, config.brick_width, config.brick_height)
            for i in range(int(config.window_width / config.brick_width))
            for j in range(int(config.window_height / 2 / config.brick_height))
        ]
