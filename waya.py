#!/usr/bin/env python3
from manim import *
import numpy as np

class FluidSimulation(Scene):
    def construct(self):
        # 标题
        title = Text("流体动力学模拟", font="SimSun", font_size=48)
        self.play(Write(title))
        self.wait()
        self.play(title.animate.to_edge(UP).scale(0.6))
        
        # 创建流体容器
        container = Rectangle(height=5, width=8, color=BLUE_E, fill_opacity=0.2)
        container.set_stroke(BLUE, 2)
        self.play(Create(container))
        
        # 流体粒子
        num_particles = 100
        particles = VGroup()
        
        # 创建随机分布的粒子
        for i in range(num_particles):
            x = np.random.uniform(-3.5, 3.5)
            y = np.random.uniform(-2, 2)
            particle = Dot(point=[x, y, 0], radius=0.05, color=BLUE)
            particles.add(particle)
        
        self.play(FadeIn(particles))
        
        # 流体动力学方程
        equation = MathTex(
            r"\frac{\partial \mathbf{u}}{\partial t} + (\mathbf{u} \cdot \nabla)\mathbf{u} = -\frac{1}{\rho}\nabla p + \nu \nabla^2 \mathbf{u} + \mathbf{g}"
        ).next_to(title, DOWN)
        
        self.play(Write(equation))
        self.wait()
        
        # 模拟流体运动
        def fluid_update(particles, dt):
            # 模拟简单的流体运动
            for particle in particles:
                # 获取当前位置
                pos = particle.get_center()
                x, y = pos[0], pos[1]
                
                # 计算新的速度和位置
                # 使用简化的流体模型：涡流 + 重力 + 边界反弹
                vx = 0.3 * np.sin(y * 0.5 + dt * 0.2) + 0.1 * np.random.randn()
                vy = 0.2 * np.cos(x * 0.5) - 0.05 + 0.1 * np.random.randn()  # 轻微向下的重力
                
                # 更新位置
                new_x = x + vx * dt
                new_y = y + vy * dt
                
                # 边界检查
                if new_x < -3.8:
                    new_x = -3.8
                    vx = -vx * 0.8  # 反弹并损失一些能量
                elif new_x > 3.8:
                    new_x = 3.8
                    vx = -vx * 0.8
                
                if new_y < -2.3:
                    new_y = -2.3
                    vy = -vy * 0.8
                elif new_y > 2.3:
                    new_y = 2.3
                    vy = -vy * 0.8
                
                # 应用新位置
                particle.move_to([new_x, new_y, 0])
                
                # 根据速度更改颜色 - 修复这里的错误
                speed = np.sqrt(vx**2 + vy**2)
                # 将浮点数转换为整数，确保 color_gradient 函数接收整数参数
                color_index = int(min(3, speed * 5))  # 限制在 0-3 范围内
                colors = [BLUE_E, BLUE, BLUE_A, WHITE]
                if color_index >= len(colors):
                    color_index = len(colors) - 1
                particle.set_color(colors[color_index])
        
        # 添加一个障碍物
        obstacle = Circle(radius=0.8, color=RED_E, fill_opacity=0.8)
        obstacle.move_to([-1, 0, 0])
        self.play(Create(obstacle))
        
        # 添加流体流动的指示箭头
        arrows = VGroup()
        for i in range(10):
            for j in range(6):
                x = -4 + i * 0.9
                y = -2.5 + j * 1
                arrow = Arrow(
                    start=[x, y, 0],
                    end=[x + 0.5, y, 0],
                    color=BLUE_A,
                    buff=0,
                    stroke_width=2,
                    max_tip_length_to_length_ratio=0.3
                )
                arrows.add(arrow)
        
        self.play(FadeIn(arrows))
        
        # 更新箭头方向以显示流场
        def arrow_updater(arrows, dt):
            for arrow in arrows:
                pos = arrow.get_start()
                x, y = pos[0], pos[1]
                
                # 计算流场方向
                angle = np.sin(y * 0.5 + dt * 0.2) * 0.5
                length = 0.5 + 0.2 * np.sin(x * 0.3 + dt * 0.1)
                
                # 避开障碍物
                dx = x - obstacle.get_center()[0]
                dy = y - obstacle.get_center()[1]
                dist = np.sqrt(dx**2 + dy**2)
                if dist < 1.5:
                    # 障碍物附近的流场偏转
                    angle += 0.5 * np.arctan2(dy, dx)
                    length *= (dist / 1.5)
                
                # 更新箭头
                end_x = x + length * np.cos(angle)
                end_y = y + length * np.sin(angle)
                arrow.put_start_and_end_on([x, y, 0], [end_x, end_y, 0])
                
                # 根据速度更改颜色 - 修复这里的错误
                color_index = int(min(1, length * 2))  # 0 或 1
                colors = [BLUE_E, BLUE_A]
                arrow.set_color(colors[color_index])
        
        # 添加波浪效果
        waves = VGroup()
        num_waves = 20
        for i in range(num_waves):
            wave = ParametricFunction(
                lambda t: np.array([
                    t - 4,  # x 从 -4 到 4
                    0.2 * np.sin(3 * t + i * 0.3) - 2,  # y 值，底部波浪
                    0
                ]),
                t_range=np.array([0, 8]),
                color=BLUE_A,
                stroke_width=2,
                stroke_opacity=0.7
            )
            waves.add(wave)
        
        self.play(Create(waves))
        
        # 波浪动画更新函数
        def wave_updater(waves, dt):
            for i, wave in enumerate(waves):
                wave.become(
                    ParametricFunction(
                        lambda t: np.array([
                            t - 4,
                            0.2 * np.sin(3 * t + i * 0.3 + self.time * 2) - 2,
                            0
                        ]),
                        t_range=np.array([0, 8]),
                        color=BLUE_A,
                        stroke_width=2,
                        stroke_opacity=0.7
                    )
                )
        
        # 添加动画更新器
        particles.add_updater(fluid_update)
        arrows.add_updater(arrow_updater)
        waves.add_updater(wave_updater)
        
        # 运行模拟
        self.wait(10)
        
        # 移除更新器
        particles.remove_updater(fluid_update)
        arrows.remove_updater(arrow_updater)
        waves.remove_updater(wave_updater)
        
        # 结束动画
        conclusion = Text("流体动力学模拟完成", font="SimSun", font_size=36)
        conclusion.to_edge(DOWN)
        self.play(Write(conclusion))
        self.wait(2)
        
        self.play(
            FadeOut(particles),
            FadeOut(container),
            FadeOut(obstacle),
            FadeOut(arrows),
            FadeOut(waves),
            FadeOut(equation),
            FadeOut(title),
            FadeOut(conclusion)
        )


class WaterDropEffect(Scene):
    def construct(self):
        # 标题
        title = Text("水滴效果模拟", font="SimSun", font_size=48)
        self.play(Write(title))
        self.wait()
        self.play(title.animate.to_edge(UP))
        
        # 创建水池
        pool = Rectangle(height=4, width=8, color=BLUE, fill_opacity=0.3)
        pool.move_to(DOWN)
        
        # 水面
        water_surface = Line(
            start=pool.get_corner(UL) + DOWN * 0.5,
            end=pool.get_corner(UR) + DOWN * 0.5,
            color=BLUE_A,
            stroke_width=3
        )
        
        self.play(Create(pool), Create(water_surface))
        
        # 创建水滴
        def create_drop(position, size=0.2):
            drop = Circle(radius=size, color=BLUE, fill_opacity=0.8)
            drop.move_to(position)
            return drop
        
        # 水滴下落动画
        def drop_animation(position):
            drop = create_drop(position + UP * 3)
            
            # 下落轨迹
            drop_path = TracedPath(drop.get_center, stroke_width=1, stroke_color=BLUE_A, stroke_opacity=0.5)
            self.add(drop_path)
            
            # 下落动画
            fall_time = 0.5
            self.play(drop.animate.move_to(position), run_time=fall_time, rate_func=rate_functions.ease_in_cubic)
            
            # 创建水波
            ripples = VGroup()
            num_ripples = 5
            max_radius = 2
            
            for i in range(num_ripples):
                ripple = Circle(radius=0.1, color=BLUE_A, stroke_opacity=(num_ripples - i) / num_ripples)
                ripple.move_to(position)
                ripples.add(ripple)
            
            # 水波扩散动画
            self.play(
                FadeOut(drop),
                FadeOut(drop_path),
                *[ripple.animate.scale(max_radius * (i + 1) / num_ripples) for i, ripple in enumerate(ripples)],
                *[ripple.animate.set_stroke(opacity=0) for ripple in ripples],
                run_time=1.5,
                rate_func=rate_functions.ease_out_sine
            )
            
            self.remove(ripples)
        
        # 多个水滴动画
        positions = [
            UP * 0.5 + LEFT * 2,
            UP * 0.5,
            UP * 0.5 + RIGHT * 2,
            UP * 0.5 + LEFT * 1,
            UP * 0.5 + RIGHT * 1
        ]
        
        for pos in positions:
            drop_animation(pos)
            self.wait(0.5)
        
        # 结束动画
        self.play(
            FadeOut(pool),
            FadeOut(water_surface),
            FadeOut(title)
        )
