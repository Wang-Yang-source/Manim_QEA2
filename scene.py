from manim import Scene, Text, MathTex, VGroup, VMobject, Create, FadeOut, Write, DOWN, UP, LEFT, RIGHT, ORIGIN, PI, Arc, Line, Circle, Rectangle, Square, Arrow, YELLOW, GRAY, BLUE, GREEN, RED, WHITE, BLACK, ORANGE, RED_E, GREEN_E, BLUE_E, Table
import numpy as np

class KirchhoffsLaws(Scene):
    def construct(self):
        # 标题：电路与机械系统建模
        title = Text("Circuit and Mechanical System Modeling", font_size=48)
        self.play(Write(title))
        self.wait()
        self.play(FadeOut(title))
        
        # 基尔霍夫电流定律 (KCL)
        kcl_title = Text("Kirchhoff's Current Law (KCL)", font_size=40)
        kcl_formula = MathTex(r"\sum_{k=1}^{n} I_k = 0", font_size=36)
        kcl_explanation = Text("Sum of currents at a node equals zero", font_size=30)
        
        kcl_group = VGroup(kcl_title, kcl_formula, kcl_explanation).arrange(DOWN, buff=0.5)
        self.play(Write(kcl_group))
        self.wait(2)
        self.play(FadeOut(kcl_group))
        
        # 基尔霍夫电压定律 (KVL)
        kvl_title = Text("Kirchhoff's Voltage Law (KVL)", font_size=40)
        kvl_formula = MathTex(r"\sum_{k=1}^{n} V_k = 0", font_size=36)
        kvl_explanation = Text("Sum of voltages around a loop equals zero", font_size=30)
        
        kvl_group = VGroup(kvl_title, kvl_formula, kvl_explanation).arrange(DOWN, buff=0.5)
        self.play(Write(kvl_group))
        self.wait(2)
        self.play(FadeOut(kvl_group))
        
        # 电路元件：电容
        capacitor_title = Text("Capacitor", font_size=40)
        capacitor_formula = MathTex(r"i_C = C \frac{dv_C}{dt}", font_size=36)
        capacitor_formula2 = MathTex(r"v_C = \frac{1}{C} \int i_C \, dt", font_size=36)
        
        capacitor_group = VGroup(capacitor_title, capacitor_formula, capacitor_formula2).arrange(DOWN, buff=0.5)
        self.play(Write(capacitor_group))
        self.wait(2)
        self.play(FadeOut(capacitor_group))
        
        # 电路元件：电感
        inductor_title = Text("Inductor", font_size=40)
        inductor_formula = MathTex(r"v_L = L \frac{di_L}{dt}", font_size=36)
        inductor_formula2 = MathTex(r"i_L = \frac{1}{L} \int v_L \, dt", font_size=36)
        
        inductor_group = VGroup(inductor_title, inductor_formula, inductor_formula2).arrange(DOWN, buff=0.5)
        self.play(Write(inductor_group))
        self.wait(2)
        self.play(FadeOut(inductor_group))
        
        # 示例电路
        self.show_example_circuit()
        
        # 机械系统建模
        self.show_mechanical_system()
        
        # 传递函数
        transfer_title = Text("Transfer Function", font_size=40)
        transfer_formula = MathTex(r"H(s) = \frac{Y_o(s)}{Y_i(s)}", font_size=36)
        
        transfer_group = VGroup(transfer_title, transfer_formula).arrange(DOWN, buff=0.5)
        self.play(Write(transfer_group))
        self.wait(2)
        self.play(FadeOut(transfer_group))
    
    def show_example_circuit(self):
        # RLC电路示例
        circuit_title = Text("RLC Circuit Example", font_size=40)
        self.play(Write(circuit_title))
        self.play(circuit_title.animate.to_edge(UP))
        
        # 创建更美观的电源图标
        source_circle = Circle(radius=0.3).set_color(BLUE)
        source_plus = Line(UP * 0.15, DOWN * 0.15, stroke_width=2).set_color(WHITE)
        source_minus = Line(LEFT * 0.15, RIGHT * 0.15, stroke_width=2).set_color(WHITE)
        source = VGroup(source_circle, source_plus, source_minus)
        
        # 改进电阻表示 - 更接近截图中的橙色矩形带刻度
        resistor = VGroup()
        resistor_base = Rectangle(height=0.2, width=0.8).set_color(ORANGE)
        for i in range(4):
            line = Line(
                LEFT * 0.4 + RIGHT * 0.2 * i,
                LEFT * 0.4 + RIGHT * 0.2 * i + UP * 0.2,
                stroke_width=2
            ).set_color(ORANGE)
            resistor.add(line)
        resistor.add(resistor_base)
        
        # 改进电感表示 - 更接近截图中的绿色螺旋
        inductor = VGroup()
        for i in range(5):
            arc = Arc(
                radius=0.1,
                start_angle=PI,
                angle=-PI,
                stroke_width=2
            ).set_color(GREEN)
            arc.shift(RIGHT * 0.2 * i)
            inductor.add(arc)
        
        # 改进电容表示 - 更接近截图中的红色双线
        capacitor = VGroup(
            Line(LEFT * 0.2, LEFT * 0.2 + UP * 0.3, stroke_width=2),
            Line(LEFT * 0.2, LEFT * 0.2 + DOWN * 0.3, stroke_width=2),
            Line(RIGHT * 0.2, RIGHT * 0.2 + UP * 0.3, stroke_width=2),
            Line(RIGHT * 0.2, RIGHT * 0.2 + DOWN * 0.3, stroke_width=2)
        ).set_color(RED)
        
        # 放置电路元件 - 按照新截图布局
        source.move_to(LEFT * 3)  # 电源在左侧
        resistor.move_to(UP * 0.5)  # 电阻在上方中间
        inductor.move_to(UP * 0.5 + RIGHT * 2)  # 电感在上方右侧
        capacitor.rotate(PI/2)  # 旋转电容使其垂直放置
        capacitor.move_to(RIGHT * 3.5)  # 电容在右侧
        
        # 调整标签位置
        source_label = MathTex("V_s").next_to(source, LEFT, buff=0.2)
        resistor_label = MathTex("R").next_to(resistor, UP, buff=0.3)
        inductor_label = MathTex("L").next_to(inductor, UP, buff=0.3)
        
        # 连接线形成矩形
        wire1 = Line(source.get_top(), LEFT * 3 + UP * 0.5, stroke_width=2)  # 从电源向上
        wire2 = Line(LEFT * 3 + UP * 0.5, resistor.get_left(), stroke_width=2)  # 左上水平线到电阻
        wire3 = Line(resistor.get_right(), inductor.get_left(), stroke_width=2)  # 电阻到电感
        wire4 = Line(inductor.get_right(), RIGHT * 3.5 + UP * 0.5, stroke_width=2)  # 电感到电容上端
        wire5 = Line(RIGHT * 3.5 + UP * 0.5, capacitor.get_top(), stroke_width=2)  # 到电容上端
        wire6 = Line(capacitor.get_bottom(), RIGHT * 3.5 + DOWN * 0.5, stroke_width=2)  # 电容下端到右下
        wire7 = Line(RIGHT * 3.5 + DOWN * 0.5, LEFT * 3 + DOWN * 0.5, stroke_width=2)  # 底部水平线
        wire8 = Line(LEFT * 3 + DOWN * 0.5, source.get_bottom(), stroke_width=2)  # 回到电源
        
        circuit = VGroup(
            source, source_label, 
            resistor, resistor_label, 
            inductor, inductor_label, 
            capacitor,
            wire1, wire2, wire3, wire4, wire5, wire6, wire7, wire8
        )
        
        # 整体居中
        circuit.move_to(ORIGIN)
        
        # 显示电路
        self.play(Create(circuit))
        
        # 电路方程 - 与截图一致
        circuit_eq = MathTex(
            r"L\frac{d^2q}{dt^2} + R\frac{dq}{dt} + \frac{1}{C}q = V_s",
            font_size=32
        ).next_to(circuit, DOWN, buff=1.2)
        
        self.play(Write(circuit_eq))
        self.wait(2)
        self.play(FadeOut(circuit), FadeOut(circuit_eq), FadeOut(circuit_title))
    
    def show_mechanical_system(self):
        # 机械系统示例
        mech_title = Text("Mechanical System Modeling", font_size=40)
        self.play(Write(mech_title))
        self.play(mech_title.animate.to_edge(UP))
        
        # 创建机械系统元件
        wall = Line(DOWN * 1.5, UP * 1.5, stroke_width=4).set_color(GRAY)
        wall.move_to(LEFT * 3.5)
        
        # 创建更接近截图的弹簧
        def create_spring(start, end, coils=10, width=0.1):
            spring = VMobject()
            points = []
            length = np.linalg.norm(end - start)
            direction = (end - start) / length
            perpendicular = np.array([-direction[1], direction[0], 0])
            
            segment_length = length / (2 * coils)
            points.append(start)
            
            for i in range(coils):
                points.append(start + direction * segment_length * (2*i + 0.5) - perpendicular * width)
                points.append(start + direction * segment_length * (2*i + 1.5) + perpendicular * width)
            
            points.append(end)
            spring.set_points_smoothly(points)
            return spring
        
        spring1 = create_spring(
            start=wall.get_right(),
            end=wall.get_right() + RIGHT * 2
        ).set_color(BLUE)
        spring1_label = MathTex("k_1").next_to(spring1, UP, buff=0.2)
        
        # 更接近截图的质量块
        mass = Square(side_length=0.8).set_color(RED).set_fill(RED_E, opacity=0.8)
        mass.next_to(spring1, RIGHT, buff=0)
        mass_label = MathTex("m").move_to(mass).set_color(WHITE)
        
        spring2 = create_spring(
            start=mass.get_right(),
            end=mass.get_right() + RIGHT * 2
        ).set_color(BLUE)
        spring2_label = MathTex("k_2").next_to(spring2, UP, buff=0.2)
        
        # 更接近截图的阻尼器
        damper_cylinder = Rectangle(height=0.6, width=1.2, fill_opacity=0.5).set_color(GREEN)
        damper_piston = Rectangle(height=0.6, width=0.2, fill_opacity=1).set_color(GREEN_E)
        
        damper = VGroup(damper_cylinder, damper_piston)
        damper_cylinder.move_to(ORIGIN)
        damper_piston.next_to(damper_cylinder, RIGHT, buff=0)
        damper.next_to(mass, DOWN, buff=1.2)
        damper_label = MathTex("c").next_to(damper, DOWN, buff=0.2)
        
        # 连接线
        line1 = Line(mass.get_bottom(), damper.get_top(), stroke_width=2)
        
        # 调整连接线位置
        line2 = Line(
            damper.get_left(), 
            wall.get_right() + DOWN * (damper.get_center()[1] - wall.get_center()[1]), 
            stroke_width=2
        )
        line3 = Line(
            damper.get_right(), 
            spring2.get_right() + DOWN * (damper.get_center()[1] - spring2.get_right()[1]), 
            stroke_width=2
        )
        
        # 位移标记和箭头 - 调整为与截图一致
        input_arrow = Arrow(
            wall.get_bottom() + DOWN * 0.2 + LEFT * 0.5,
            wall.get_bottom() + DOWN * 0.2 + RIGHT * 0.5, 
            color=YELLOW, 
            max_stroke_width_to_length_ratio=5,
            stroke_width=2
        )
        input_label = MathTex("y_i").next_to(input_arrow, DOWN, buff=0.1)
        
        output_arrow = Arrow(
            damper.get_right() + RIGHT * 0.2, 
            damper.get_right() + RIGHT * 1.2, 
            color=YELLOW, 
            max_stroke_width_to_length_ratio=5,
            stroke_width=2
        )
        output_label = MathTex("y_o").next_to(output_arrow, DOWN, buff=0.1)
        
        # 移除坐标系，使其更接近截图
        
        mech_system = VGroup(
            wall, spring1, spring1_label, mass, mass_label, 
            spring2, spring2_label, damper, damper_label,
            line1, line2, line3, input_arrow, input_label, output_arrow, output_label
        )
        
        # 整体居中
        mech_system.move_to(ORIGIN)
        
        # 显示机械系统
        self.play(Create(mech_system))
        
        # 添加机械系统方程 - 调整位置更接近截图底部
        self.wait(1)
        
        # 运动方程 - 位置调整为更接近截图底部
        mech_eq = MathTex(
            r"m\frac{d^2y_o}{dt^2} + c\frac{dy_o}{dt} + k_1(y_o-y_i) + k_2y_o = 0",
            font_size=32
        ).move_to(DOWN * 3)  # 直接定位到底部
        
        self.play(Write(mech_eq))
        self.wait(2)
        
        # 不显示传递函数，与截图保持一致
        self.play(FadeOut(mech_system), FadeOut(mech_eq), FadeOut(mech_title))


class MechanicalElectricalAnalogy(Scene):
    def construct(self):
        title = Text("Mechanical-Electrical System Duality", font_size=48)
        self.play(Write(title))
        self.wait()
        self.play(title.animate.to_edge(UP))
        
        # 创建对偶表格
        table = Table(
            [["Mechanical", "Electrical"],
             ["Displacement (x)", "Charge (q)"],
             ["Velocity (v)", "Current (i)"],
             ["Force (F)", "Voltage (V)"],
             ["Mass (m)", "Inductance (L)"],
             ["Spring constant (k)", "Inverse capacitance (1/C)"],
             ["Damping coefficient (c)", "Resistance (R)"]],
            row_labels=[Text("") for _ in range(7)],
            col_labels=[Text("") for _ in range(2)],
            include_outer_lines=True
        )
        
        self.play(Create(table))
        self.wait(2)
        
        # 机械系统方程
        mech_eq = MathTex(
            r"m\frac{d^2x}{dt^2} + c\frac{dx}{dt} + kx = F(t)",
            font_size=36
        ).next_to(table, DOWN, buff=1)
        
        self.play(Write(mech_eq))
        self.wait(1)
        
        # 电气系统方程
        elec_eq = MathTex(
            r"L\frac{d^2q}{dt^2} + R\frac{dq}{dt} + \frac{1}{C}q = V(t)",
            font_size=36
        ).next_to(mech_eq, DOWN, buff=0.5)
        
        self.play(Write(elec_eq))
        self.wait(2)
        
        self.play(FadeOut(table), FadeOut(mech_eq), FadeOut(elec_eq), FadeOut(title))
