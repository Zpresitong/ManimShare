from manim import *

class ChineseChess(Scene):
    def construct(self):
        filename = "棋谱示例.txt"
        self.camera.background_color = WHITE
        # 初始化棋盘和棋子
        self.board_width = 5.5  # 棋盘宽度
        self.board_height = 6 # 棋盘高度
        self.main_board = self.draw_board(self.board_width, self.board_height)
        # 添加河界文字
        self.river_text = Text("楚河          汉界", font="SimHei", font_size=28, color=BLACK).set_z_index(-1).move_to([0, 0, 0])
        # 绘制棋盘
        self.play(Write(self.river_text), run_time=0.5)
        self.play(VGroup(self.main_board, self.river_text).animate.shift(LEFT*1.5), run_time=0.5)
        # 记录双方信息
        red_name, black_name = self.add_players(filename=filename)
        red_name.move_to(self.main_board.get_bottom()).shift(DOWN*0.6 + 3*LEFT)
        black_name.move_to(self.main_board.get_top()).shift(UP*0.6 + 3*LEFT)
        self.play(Write(red_name), Write(black_name))
        # 绘制棋子
        self.pieces = self.add_pieces(self.main_board, filename=filename)
        self.wait()

        # 读取棋谱并动态展示
        self.step_time = 1 # 设置主棋步动画时长
        self.sub_time = 0.25 # 设置注释棋步动画时长
        self.steps, self.comments = self.read_step_from_file(filename)

        sub_step_clus = []
        sub_step = []
        for s_id in range(1, len(self.steps)):
            if self.steps[s_id][1] == 0 and s_id > 1:
                sub_step_clus.append(sub_step)
                sub_step = [s_id]
            else:
                sub_step.append(s_id)
        sub_step_clus.append(sub_step)

        self.move_steps = []
        if len(sub_step_clus[0]) == 0:
            self.move_steps += self.play_moves_from_notation(self.main_board, self.pieces, self.steps, 0, self.comments, 1,)
        else:
            start_step = 1
            for sub_step in list(reversed(sub_step_clus)):
                pause_step_id = sub_step[0]
                pause_step = self.steps[pause_step_id][-1]
                record_pause_step = pause_step
                self.move_steps += self.play_moves_from_notation(self.main_board, self.pieces, self.steps, 0, self.comments, start_step, pause_step)
                temp_scene = Group(self.main_board.copy(), self.river_text.copy())
                pieces_group = Group()
                for pieces in self.pieces:
                    for piece_id in pieces:
                        temp_scene.add(pieces[piece_id].copy())
                        pieces_group.add(pieces[piece_id])
                try:
                    center = self.main_board.get_center()
                    board_width = (self.main_board.get_right() - self.main_board.get_left())[0]
                    board_height = (self.main_board.get_top() - self.main_board.get_bottom())[1]
                    line_spacing_x = board_width / 8  # 竖线间距
                    line_spacing_y = board_height / 9  # 横线间距
                    t_start_x, t_start_y, t_end_x, t_end_y = self.move_steps[-1]['move_site']
                    start_pos = center + (t_start_x * line_spacing_x, t_start_y * line_spacing_y, 0)
                    end_pos = center + (t_end_x * line_spacing_x, t_end_y * line_spacing_y, 0)
                    t_start_tracks = self.construct_tracks().scale(line_spacing_x / 2 - 0.04).move_to(start_pos).set_z_index(
                        1)
                    t_end_tracks = self.construct_tracks().scale(line_spacing_x / 2 - 0.04).move_to(end_pos).set_z_index(1)
                    temp_scene.add(t_start_tracks, t_end_tracks)
                except:
                    pass
                change_title = Text("变招", font="SimHei", font_size=28, color=BLACK).set_z_index(-1).move_to(RIGHT*4+UP*3.5)
                self.add(temp_scene)
                self.play(Group(self.main_board, pieces_group, self.river_text).animate.scale(0.8).shift(RIGHT*5.5+UP*0.5),
                          Write(change_title),
                          temp_scene.animate.shift(LEFT))
                for s_id in list(reversed(sub_step)):
                    self.move_steps += self.play_moves_from_notation(self.main_board, self.pieces, self.steps, s_id,
                                                                     self.comments, pause_step)
                    pause_step = self.steps[s_id][-1]
                    self.reverse_step(self.move_steps, self.pieces, self.main_board, pause_step - 1, run_time=1)
                self.play(Group(self.main_board, pieces_group, self.river_text).animate.shift(-(RIGHT*5.5+UP*0.5)).scale(1.25),
                          Unwrite(change_title),
                          temp_scene.animate.shift(RIGHT))
                self.remove(temp_scene)
                start_step = record_pause_step
            self.move_steps += self.play_moves_from_notation(self.main_board, self.pieces, self.steps, 0, self.comments,
                                                             start_step,)

    def draw_board(self, board_width, board_height):
        line_spacing_x = board_width / 8  # 竖线间距
        line_spacing_y = board_height / 9  # 横线间距
        """绘制棋盘"""
        board = VGroup()
        # 绘制竖线（9条）
        for i, x in enumerate(np.linspace(-board_width / 2 + line_spacing_x, board_width / 2 - line_spacing_x, 7)):
            board.add(Line([x, board_height / 2, 0], [x, 0.5 * line_spacing_y, 0], color=BLACK))

        for i, x in enumerate(np.linspace(-board_width / 2 + line_spacing_x, board_width / 2 - line_spacing_x, 7)):
            board.add(Line([x, -0.5 * line_spacing_y, 0], [x, -board_height / 2, 0], color=BLACK))

        for i, x in enumerate(np.linspace(-board_width / 2, board_width / 2, 2)):
            board.add(Line([x, board_height / 2, 0], [x, -board_height / 2, 0], color=BLACK))

        # 绘制横线（10条）
        for y in np.linspace(-board_height / 2, board_height / 2, 10):
            board.add(Line([-board_width / 2, y, 0], [board_width / 2, y, 0], color=BLACK))

        # 绘制九宫斜线
        board.add(self.draw_palace(-board_height / 2, line_spacing_x, line_spacing_y))  # 红方九宫
        board.add(self.draw_palace(board_height / 2, line_spacing_x, line_spacing_y)) # 黑方九宫

        # 添加棋子摆放点
        posi = VGroup(Line([1, 0.25, 0], [0.25, 0.25, 0], color=BLACK), Line([0.25, 1, 0], [0.25, 0.25, 0], color=BLACK),
                      Line([-1, -0.25, 0], [-0.25, -0.25, 0], color=BLACK), Line([-0.25, -1, 0], [-0.25, -0.25, 0], color=BLACK),
                      Line([-1, 0.25, 0], [-0.25, 0.25, 0], color=BLACK), Line([-0.25, 1, 0], [-0.25, 0.25, 0], color=BLACK),
                      Line([1, -0.25, 0], [0.25, -0.25, 0], color=BLACK), Line([0.25, -1, 0], [0.25, -0.25, 0], color=BLACK),)
        sites = [(-3, -2.5), (3, -2.5), (-4, -1.5), (-2, -1.5), (0, -1.5), (2, -1.5), (4, -1.5),
                 (-3, 2.5), (3, 2.5), (-4, 1.5), (-2, 1.5), (0, 1.5), (2, 1.5), (4, 1.5),]
        for x, y in sites:
            if x == -4:
                temp_posi = posi.copy().scale(0.25).move_to([x * line_spacing_x, y * line_spacing_y, 0])
                board.add(temp_posi[0], temp_posi[1], temp_posi[6], temp_posi[7])
            elif x == 4:
                temp_posi = posi.copy().scale(0.25).move_to([x * line_spacing_x, y * line_spacing_y, 0])
                board.add(temp_posi[2], temp_posi[3], temp_posi[4], temp_posi[5])
            else:
                board.add(posi.copy().scale(0.25).move_to([x * line_spacing_x, y * line_spacing_y, 0]))

        self.add(board)

        return board

    def draw_palace(self, base_y, line_spacing_x, line_spacing_y):
        """绘制九宫斜线"""
        middle_y = base_y + line_spacing_y if base_y < 0 else base_y - line_spacing_y
        top_y = base_y + 2 * line_spacing_y if base_y < 0 else base_y - 2 * line_spacing_y

        return VGroup(
            Line([-line_spacing_x, base_y, 0], [0, middle_y, 0], color=BLACK),
            Line([0, middle_y, 0], [line_spacing_x, base_y, 0], color=BLACK),
            Line([-line_spacing_x, top_y, 0], [0, middle_y, 0], color=BLACK),
            Line([0, middle_y, 0], [line_spacing_x, top_y, 0], color=BLACK)
        )

    def add_players(self, filename=None):
        red_name, black_name = '', ''
        if not filename:
            pass
        else:
            with open(filename, "r", encoding="utf-8") as file:
                textlines = file.readlines()

            for textline in textlines: # 双方信息
                if '红方: ' in textline:
                    red_name = textline.strip('红方: ').strip('\n')
                elif '黑方: ' in textline:
                    black_name = textline.strip('黑方: ').strip('\n')
                elif '[DhtmlXQ_red]' in textline:
                    red_name = textline.strip('[DhtmlXQ_red]').strip('\n').strip('[/DhtmlXQ_red]')
                elif '[DhtmlXQ_black]' in textline:
                    black_name = textline.strip('[DhtmlXQ_black]').strip('\n').strip('[/DhtmlXQ_black]')

        return Text(red_name, font="SimHei", font_size=28, color=BLACK), Text(black_name, font="SimHei", font_size=28, color=BLACK)


    def add_pieces(self, board, filename = None):
        center = board.get_center()
        board_width = (board.get_right() - board.get_left())[0]
        board_height = (board.get_top() - board.get_bottom())[1]
        line_spacing_x = board_width / 8  # 竖线间距
        line_spacing_y = board_height / 9  # 横线间距

        """初始化棋子"""
        # 红方棋子配置
        red_pieces = [
            ("帥", 0, -4.5), ("仕", -1, -4.5), ("仕", 1, -4.5),
            ("相", -2, -4.5), ("相", 2, -4.5), ("傌", -3, -4.5),
            ("傌", 3, -4.5), ("俥", -4, -4.5), ("俥", 4, -4.5),
            ("炮", -3, -2.5), ("炮", 3, -2.5),
            ("兵", -4, -1.5), ("兵", -2, -1.5), ("兵", 0, -1.5),
            ("兵", 2, -1.5), ("兵", 4, -1.5)
        ]

        # 黑方棋子配置
        black_pieces = [
            ("將", 0, 4.5), ("士", -1, 4.5), ("士", 1, 4.5),
            ("象", -2, 4.5), ("象", 2, 4.5), ("馬", -3, 4.5),
            ("馬", 3, 4.5), ("車", -4, 4.5), ("車", 4, 4.5),
            ("砲", -3, 2.5), ("砲", 3, 2.5),
            ("卒", -4, 1.5), ("卒", -2, 1.5), ("卒", 0, 1.5),
            ("卒", 2, 1.5), ("卒", 4, 1.5)
        ]

        if not filename:
            pass
        else:
            with open(filename, "r", encoding="utf-8") as file:
                textlines = file.readlines()
            situations = None
            for textline in textlines:
                if "开始局面" in textline or " w" in textline or " b" in textline or '[DhtmlXQ_fen]' in textline:
                    for string in textline.strip('[DhtmlXQ_fen]').split(" "):
                        if "/" in string:
                            situations = string.split("/")
                            break
                    break
                elif '[DhtmlXQ_binit]' in textline:
                    situations = textline.strip('[DhtmlXQ_binit]').strip("\n").strip("[/DhtmlXQ_binit]")
                    break

            if not situations:
                pass
            else:
                """初始化棋子"""
                # 红方棋子配置
                red_pieces = []
                # 黑方棋子配置
                black_pieces = []

                if isinstance(situations, list):
                    piece_to_char = {
                        'r': '車', 'n': '馬', 'b': '象', 'a': '士', 'k': '將', 'p': '卒', 'c': '砲',
                        'R': '俥', 'N': '傌', 'B': '相', 'A': '仕', 'K': '帥', 'P': '兵', 'C': '炮',
                    }
                    for row in range(len(situations)):
                        col = 0
                        for char in situations[row]:
                            if char.isdigit():
                                col += int(char)
                            else:
                                x = col - 4  # 转换为棋盘x坐标
                                y = 4.5 - row    # 转换为棋盘y坐标
                                black_pieces.append((piece_to_char[char], x, y)) if char.islower() else red_pieces.append((piece_to_char[char], x, y))
                                col += 1
                elif isinstance(situations, str):
                    piece_chars = '俥傌相仕帥仕相傌俥炮炮兵兵兵兵兵車馬象士將士象馬車砲砲卒卒卒卒卒'
                    for i in range(len(piece_chars)):
                        char, col, row = piece_chars[i], int(situations[2 * i]), int(situations[2 * i + 1])
                        if col == 9 and row == 9:
                            continue
                        else:
                            x = col - 4  # 转换为棋盘x坐标
                            y = 4.5 - row  # 转换为棋盘y坐标
                            black_pieces.append((char, x, y)) if i >= 16 else red_pieces.append((char, x, y))
                            col += 1

        # 创建棋子函数
        def create_piece(char, color):
            return VGroup(
                Circle(radius=line_spacing_x/2-0.04, color=color, fill_color=WHITE, fill_opacity=1),
                Text(char, font="SimHei", font_size=int(line_spacing_x*52), color=color)
            )

        pieces = VGroup()
        # 添加红方棋子
        r_pieces = {}
        for char, x, y in red_pieces:
            piece = create_piece(char, RED).move_to(center + [x * line_spacing_x, y * line_spacing_y, 0])
            r_pieces[(x, y)] = piece
            pieces.add(piece)

        # 添加黑方棋子
        b_pieces = {}
        for char, x, y in black_pieces:
            piece = create_piece(char, BLACK).move_to(center + [x * line_spacing_x, y * line_spacing_y, 0])
            b_pieces[(x, y)] = piece
            pieces.add(piece)

        self.play(Create(pieces))

        return r_pieces, b_pieces

    def play_moves_from_notation(self, board, pieces, steps, step_id, comments, start_step, end_step=None):
        digitals = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
                    '１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9,
                    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
        red_char = {'车': '俥', '马': '傌', '相': '相', '仕': '仕', '士': '仕', '帅': '帥', '兵': '兵',
                    '炮': '炮', }
        black_char = {'车': '車', '马': '馬', '象': '象', '士': '士', '将': '將', '卒': '卒', '炮': '砲',
                      '砲': '砲', }
        red_dig = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
        black_dig = {'１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9,
                     '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}

        move_steps = []

        red_pieces, black_pieces = pieces
        pieces_board = VGroup(board)
        for ind in red_pieces:
            pieces_board.add(red_pieces[ind])
        for ind in black_pieces:
            pieces_board.add(black_pieces[ind])
        if isinstance(steps[step_id][-1], int): #东萍棋谱格式
            step_start_index = start_step
            if end_step:
                sub_steps = steps[step_id][0][(step_start_index-1)*4:(end_step-1)*4]
            else:
                sub_steps = steps[step_id][0][(step_start_index - 1) * 4:]
            count = step_start_index - 1
            for i in range(0, len(sub_steps), 4):
                start_x, start_y = int(sub_steps[i]) - 4, 4.5 - int(sub_steps[i+1])
                end_x, end_y = int(sub_steps[i + 2]) - 4, 4.5 - int(sub_steps[i + 3])

                if red_pieces.get((start_x, start_y)):
                    piece = red_pieces.get((start_x, start_y))
                    pieces_dict = red_pieces
                    opponent_dict = black_pieces
                    is_red = True
                elif black_pieces.get((start_x, start_y)):
                    piece = black_pieces.get((start_x, start_y))
                    pieces_dict = black_pieces
                    opponent_dict = red_pieces
                    is_red = False
                else:
                    print(f"未找到棋子")
                    continue

                count += 1
                try:
                    self.remove(t_start_tracks, t_end_tracks)
                    self.play(FadeOut(s_board_pieces, temp_tracks, background, comm_text))
                    del s_board_pieces, temp_tracks
                    del s_start_tracks, s_end_tracks
                except:
                    pass
                t_start_tracks, t_end_tracks, move_step = self.piece_move(piece, pieces_dict, opponent_dict, [start_x, start_y, end_x, end_y], board=self.main_board, run_time=self.step_time)
                move_steps.append(move_step)
                temp_tracks = VGroup(t_start_tracks.copy(), t_end_tracks.copy())

                comment = comments.get((step_id, count))
                if comment:
                    comment_steps = comment.split("||")
                    for comment_step in comment_steps:
                        try:
                            self.play(FadeOut(s_board_pieces, background, comm_text))
                            del s_board_pieces, s_start_tracks, s_end_tracks
                        except:
                            pass
                        step_cont = False
                        for j in range(len(comment_step)):
                            s_step = comment_step[j:j + 4]
                            if len(s_step) < 4:
                                break
                            elif s_step[2] in ['平', '进', '退'] and s_step[-1] in digitals:
                                step_cont = True
                        if not step_cont:
                            com_text = Text(comment_step, font="SimHei", font_size=16, color=BLACK).move_to(RIGHT*3.5+DOWN*2.5)
                            self.add(com_text)
                            self.wait(1)
                            self.remove(com_text)
                            continue
                        try:
                            self.add(temp_tracks)
                        except:
                            pass
                        pieces_board.set_z_index(0)

                        sub_board = board.copy().set_style(stroke_width=2)
                        sub_center = sub_board.get_center()
                        sub_board_width = (sub_board.get_right() - sub_board.get_left())[0]
                        sub_board_height = (sub_board.get_top() - sub_board.get_bottom())[1]
                        background = Rectangle(color=GREY_A, width=sub_board_width*1.2, height=sub_board_height*1.4, fill_color=GREY_A,
                                               fill_opacity=1).move_to(sub_center).set_z_index(1)
                        comm_text = Text('注释演绎', font="SimHei", font_size=sub_board_width*5, color=BLACK).move_to(sub_board.get_top()).shift(UP*0.5).set_z_index(1)
                        s_red_pieces, s_black_pieces = {}, {}
                        s_board_pieces = VGroup()
                        s_board_pieces.add(sub_board)
                        for index in red_pieces:
                            s_pieces = red_pieces[index].copy()
                            s_pieces[0].set_style(stroke_width=2)
                            s_board_pieces.add(s_pieces)
                            s_red_pieces[index] = s_pieces
                        for index in black_pieces:
                            s_pieces = black_pieces[index].copy()
                            s_pieces[0].set_style(stroke_width=2)
                            s_board_pieces.add(s_pieces)
                            s_black_pieces[index] = s_pieces
                        s_board_pieces.set_z_index(2)
                        self.add(background, comm_text)
                        self.play(VGroup(background, comm_text, s_board_pieces).animate.scale_to_fit_width(4.5).move_to(RIGHT*4+UP*0.5))
                        sub_count = 0
                        for j in range(len(comment_step)):
                            s_step = comment_step[j:j+4]
                            if len(s_step) < 4:
                                break
                            elif s_step[2] in ['平', '进', '退'] and s_step[-1] in digitals:
                                if (s_step[0] in red_char or s_step[0] in black_char) and s_step[1] in digitals:
                                    sub_count += 1
                                    pass
                                elif s_step[0] in ['前', '二', '中', '三', '四', '后'] and (s_step[1] in red_char or s_step[1] in black_char):
                                    sub_count += 1
                                    pass
                                elif s_step[0] in ['前', '二', '中', '三', '四', '后'] and s_step[1] in digitals:
                                    sub_count += 1
                                    pass
                                else:
                                    continue

                                if s_step[-1] in red_dig:
                                    s_is_red = True
                                elif s_step[-1] in black_dig:
                                    s_is_red = False

                                if s_is_red:
                                    s_pieces_dict = s_red_pieces
                                    s_opponent_dict = s_black_pieces
                                else:
                                    s_pieces_dict = s_black_pieces
                                    s_opponent_dict = s_red_pieces
                                if sub_count == 1 and is_red == s_is_red:
                                    temp_step = {}
                                    temp_psx, temp_psy, temp_pex, temp_pey = move_step['move_site']
                                    if s_red_pieces.get((temp_pex, temp_pey)):
                                        temp_step['move_piece'] = s_red_pieces.get((temp_pex, temp_pey))
                                    elif s_black_pieces.get((temp_pex, temp_pey)):
                                        temp_step['move_piece'] = s_black_pieces.get((temp_pex, temp_pey))
                                    temp_step['move_site'] = move_step['move_site']
                                    if move_step.get('target_piece'):
                                        sub_center = sub_board.get_center()
                                        sub_board_width = (sub_board.get_right() - sub_board.get_left())[0]
                                        sub_board_height = (sub_board.get_top() - sub_board.get_bottom())[1]
                                        sub_line_spacing_x = sub_board_width / 8  # 竖线间距
                                        sub_line_spacing_y = sub_board_height / 9  # 横线间距
                                        scale_fa = sub_board_width/(board.get_right()-board.get_left())[0]
                                        sub_end_pos = sub_center + (temp_pex * sub_line_spacing_x, temp_pey * sub_line_spacing_y, 0)
                                        temp_step['target_piece'] = move_step['target_piece'].copy().scale(scale_fa).move_to(sub_end_pos)
                                        temp_step['target_piece'][0].set_style(stroke_width=2)
                                        s_board_pieces.add(temp_step['target_piece'])
                                    self.reverse_step([temp_step], [s_red_pieces, s_black_pieces], sub_board, 0, run_time=1)
                                    s_start_x, s_start_y, s_end_x, s_end_y = self.step_conv(s_step, s_red_pieces, s_black_pieces)
                                    s_piece = s_pieces_dict.get((s_start_x, s_start_y))
                                else:
                                    s_start_x, s_start_y, s_end_x, s_end_y = self.step_conv(s_step, s_red_pieces, s_black_pieces)
                                    s_piece = s_pieces_dict.get((s_start_x, s_start_y))
                                s_start_tracks, s_end_tracks = self.piece_move(s_piece, s_pieces_dict, s_opponent_dict,
                                                                          [s_start_x, s_start_y, s_end_x, s_end_y],
                                                                          board=sub_board, run_time=self.sub_time)[0:2]
                                self.remove(s_start_tracks, s_end_tracks)


        elif isinstance(steps[step_id][-1], str): # 皮卡鱼象棋中文棋谱
            # 处理红方和黑方棋步
            for step in steps[step_id]:
                if len(step) < 4:
                    continue

                start_x, start_y, end_x, end_y = self.step_conv(step, red_pieces, black_pieces)
                if red_pieces.get((start_x, start_y)):
                    piece = red_pieces.get((start_x, start_y))
                    pieces_dict = red_pieces
                    opponent_dict = black_pieces
                elif black_pieces.get((start_x, start_y)):
                    piece = black_pieces.get((start_x, start_y))
                    pieces_dict = black_pieces
                    opponent_dict = red_pieces
                else:
                    print(f"未找到棋子")
                    continue
                try:
                    self.remove(t_start_tracks, t_end_tracks)
                except:
                    pass
                t_start_tracks, t_end_tracks, move_step = self.piece_move(piece, pieces_dict, opponent_dict, [start_x, start_y, end_x, end_y], board=self.main_board, run_time=self.step_time)

                move_steps.append(move_step)

        try:
            self.wait()
            self.remove(t_start_tracks, t_end_tracks)
        except:
            pass
        return move_steps
    def step_conv(self, step, red_pieces, black_pieces): #中文步骤解析
        red_dig = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}
        black_dig = {'１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9,
                     '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}

        red_char = {'车': '俥', '马': '傌', '相': '相', '仕': '仕', '士': '仕', '帅': '帥', '兵': '兵',
                    '炮': '炮', }
        black_char = {'车': '車', '马': '馬', '象': '象', '士': '士', '将': '將', '卒': '卒', '炮': '砲',
                      '砲': '砲', }

        # 确定阵营和参数
        if step[-1] in red_dig:
            pieces_dict = red_pieces
            dig_map = red_dig
            char_map = red_char
            is_r = 1
            is_red = True
            rows = [-4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5]
        elif step[-1] in black_dig:
            pieces_dict = black_pieces
            dig_map = black_dig
            char_map = black_char
            is_r = -1
            is_red = False
            rows = list(reversed([-4.5, -3.5, -2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 3.5, 4.5]))
        else:
            return 0

        # 解析棋步参数
        if step[0] in char_map and step[-1] in dig_map:
            piece_type = step[0]
            start_col = step[1]
            move_type = step[2]
            move_amount = step[3]

            # 计算起始坐标
            try:
                start_x = is_r * (5 - dig_map[start_col])
            except KeyError:
                print(f"无效列坐标: {start_col}")
                return 0

            # 寻找起始y坐标
            found = False
            if char_map[piece_type] in ['士', '仕', '象', '相'] and move_type == '退':
                for y in list(reversed(rows)):
                    piece = pieces_dict.get((start_x, y))
                    if piece and piece[1].text == char_map[piece_type]:
                        start_y = y
                        found = True
                        break
            else:
                for y in rows:
                    piece = pieces_dict.get((start_x, y))
                    if piece and piece[1].text == char_map[piece_type]:
                        start_y = y
                        found = True
                        break

            if not found:
                print(f"未找到棋子 {char_map[piece_type]} 在 ({start_x}, ?)")
                return 0

        elif step[1] in char_map and step[1] not in ['兵', '卒'] and step[-1] in dig_map:
            cols = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
            piece_index = step[0]
            piece_type = step[1]
            move_type = step[2]
            move_amount = step[3]

            found = False
            if piece_type in ['车', '俥', '马', '傌', '炮', '砲', '車', '馬']:
                for x in cols:
                    if piece_index == '前':
                        for y in list(reversed(rows)):
                            piece = pieces_dict.get((x, y))
                            if piece and piece[1].text == char_map[piece_type]:
                                start_x, start_y = x, y
                                found = True
                                break
                    elif piece_index == '后':
                        for y in rows:
                            piece = pieces_dict.get((x, y))
                            if piece and piece[1].text == char_map[piece_type]:
                                start_x, start_y = x, y
                                found = True
                                break
                    if found:
                        break

            if not found:
                print(f"未找到棋子 {char_map[piece_type]}")
                return 0

        else:
            cols = [-4, -3, -2, -1, 0, 1, 2, 3, 4]
            piece_index = step[0]
            piece_type = ('兵' if is_red else '卒')
            move_type = step[2]
            move_amount = step[3]

            found = False
            if step[1] in dig_map:
                start_col = step[1]
                try:
                    start_x = is_r * (5 - dig_map[start_col])
                except KeyError:
                    print(f"无效列坐标: {start_col}")
                    return 0
            elif step[1] in ['兵', '卒']:
                max_count = 0
                for x in cols:
                    count = 0
                    for y in rows:
                        piece = pieces_dict.get((x, y))
                        if piece and piece[1].text == char_map[piece_type]:
                            count += 1
                    if count > max_count:
                        max_count = count
                        start_x = x
            else:
                return 0

            index_dic = {'二': 2, '三': 3, '四': 4, '中': 2}
            if piece_index == '前':
                for y in list(reversed(rows)):
                    piece = pieces_dict.get((start_x, y))
                    if piece and piece[1].text == char_map[piece_type]:
                        start_y = y
                        found = True
                        break
            elif piece_index == '后':
                for y in rows:
                    piece = pieces_dict.get((start_x, y))
                    if piece and piece[1].text == char_map[piece_type]:
                        start_y = y
                        found = True
                        break
            elif piece_index in index_dic:
                count = 0
                for y in list(reversed(rows)):
                    piece = pieces_dict.get((start_x, y))
                    if piece and piece[1].text == char_map[piece_type]:
                        count += 1
                        if count == index_dic[piece_index]:
                            start_y = y
                            found = True
                            break

            if not found:
                print(f"未找到棋子 {char_map[piece_type]}")
                return 0

        # 计算目标坐标
        if move_type == '平':
            # 横向移动
            end_x = (5 - dig_map[move_amount]) * is_r
            end_y = start_y
        else:
            # 纵向移动
            vertical_move = dig_map[move_amount]

            if piece_type in ['马', '馬', '傌']:
                # 马走日：横向移动1，纵向移动2 或者横向2，纵向1
                delta_x = abs(dig_map[start_col] - dig_map[move_amount])
                delta_y = 3 - delta_x  # 马步的特殊计算
                end_y = start_y + (delta_y * is_r if move_type == '进' else -delta_y * is_r)
                end_x = is_r * (5 - dig_map[move_amount])
            elif piece_type in ['相', '象']:
                # 相走田
                end_x = is_r * (5 - dig_map[move_amount])
                end_y = start_y + (2 * is_r if move_type == '进' else -2 * is_r)
            elif piece_type in ['仕', '士']:
                # 仕斜走
                end_x = is_r * (5 - dig_map[move_amount])
                end_y = start_y + (1 * is_r if move_type == '进' else -1 * is_r)
            else:
                # 普通进退
                end_x = start_x
                end_y = start_y + (vertical_move * is_r if move_type == '进' else -vertical_move * is_r)

        return [start_x, start_y, end_x, end_y]

    def construct_tracks(self):
        return VGroup(Line((0, 0, 0), (0.5, 0, 0), ),
                      Line((1.5, 0, 0), (2, 0, 0), ),
                      Line((2, 0, 0), (2, 0.5, 0), ),
                      Line((2, 1.5, 0), (2, 2, 0), ),
                      Line((2, 2, 0), (1.5, 2, 0), ),
                      Line((0.5, 2, 0), (0, 2, 0), ),
                      Line((0, 2, 0), (0, 1.5, 0), ),
                      Line((0, 0.5, 0), (0, 0, 0), ), ).set_color(GREEN)

    def piece_move(self, piece, pieces_dict, opponent_dict, site_list, board, run_time=1):  # 走棋动画
        move_step = {}
        center = board.get_center()
        board_width = (board.get_right() - board.get_left())[0]
        board_height = (board.get_top() - board.get_bottom())[1]
        line_spacing_x = board_width / 8  # 竖线间距
        line_spacing_y = board_height / 9  # 横线间距
        # 设置棋子图层
        move_step['move_piece'] = piece
        piece.set_z_index(2)
        start_x, start_y, end_x, end_y = site_list
        move_step['move_site'] = site_list
        # 转换实际坐标
        start_pos = center + (start_x * line_spacing_x, start_y * line_spacing_y, 0)
        end_pos = center + (end_x * line_spacing_x, end_y * line_spacing_y, 0)

        animations = []

        start_tracks = self.construct_tracks().scale(line_spacing_x / 2 - 0.04).move_to(start_pos).set_z_index(1)
        end_tracks = self.construct_tracks().scale(line_spacing_x / 2 - 0.04).move_to(start_pos).set_z_index(1)
        self.add(start_tracks, end_tracks)
        animations.append(end_tracks.animate.move_to(end_pos))

        # 移动动画
        animations.append(piece.animate.move_to(end_pos))

        # 处理吃子
        target_piece = opponent_dict.get((end_x, end_y))
        # 吃子动画
        if target_piece:
            animations.append(FadeOut(target_piece))
            move_step['target_piece'] = target_piece
            del opponent_dict[(end_x, end_y)]

        # 执行动画
        self.play(*animations, run_time=run_time / 2)
        self.wait(run_time / 2)

        # 更新棋子位置
        del pieces_dict[(start_x, start_y)]
        pieces_dict[(end_x, end_y)] = piece

        return start_tracks, end_tracks, move_step

    def reverse_step(self, move_steps, pieces, board, target_step, run_time=1):
        red_pieces_dict, black_pieces_dict = pieces
        center = board.get_center()
        board_width = (board.get_right() - board.get_left())[0]
        board_height = (board.get_top() - board.get_bottom())[1]
        line_spacing_x = board_width / 8  # 竖线间距
        line_spacing_y = board_height / 9  # 横线间距
        red_piece_chars = '俥傌相仕帥炮兵'
        black_piece_chars = '車馬象士將砲卒'

        sub_steps = move_steps[target_step:]
        animations = []
        for move_step in list(reversed(sub_steps)):
            start_x, start_y, end_x, end_y = move_step['move_site']
            move_piece = move_step['move_piece']
            if move_piece[1].text in red_piece_chars:
                pieces_dict, opponent_dict = red_pieces_dict, black_pieces_dict
            elif move_piece[1].text in black_piece_chars:
                pieces_dict, opponent_dict = black_pieces_dict, red_pieces_dict

            start_pos = center + (start_x * line_spacing_x, start_y * line_spacing_y, 0)
            end_pos = center + (end_x * line_spacing_x, end_y * line_spacing_y, 0)
            animations.append(move_piece.animate.move_to(start_pos))
            del pieces_dict[(end_x, end_y)]
            pieces_dict[(start_x, start_y)] = move_piece
            target_piece = move_step.get('target_piece')
            # 吃子动画
            if target_piece:
                target_piece.move_to(end_pos)
                animations.append(FadeIn(target_piece))
                opponent_dict[(end_x, end_y)] = target_piece

        self.play(*animations, run_time=run_time / 2)
        self.wait(run_time / 2)

        del move_steps[target_step:]

    def read_step_from_file(self, filename):
        steps = {}
        temp_step_indexes = {}
        comments = {}
        filename = "棋谱示例.txt"
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()

        if '[DhtmlXQ]' in lines[0]:  # 东萍棋谱格式
            for line in lines:
                if '[DhtmlXQ_movelist]' in line:
                    steps[0] = [line.strip('[DhtmlXQ_movelist]').strip('\n').strip('[/DhtmlXQ_movelist]'), -1, 1]
                elif '[DhtmlXQ_move_' in line:
                    step_info = line.strip('[DhtmlXQ_move_').split('[')[0].split(']')[0].split('_')
                    up_step_id, start_index, target_step_id = int(step_info[0]), int(step_info[1]), int(step_info[2])
                    t_step = line.strip('[DhtmlXQ_move_').split('[')[0].split(']')[1]
                    temp_step_indexes[target_step_id] = [up_step_id, start_index, t_step]
                elif '[DhtmlXQ_comment' in line:
                    comments_info = line.strip('[DhtmlXQ_comment').split('[')[0].split(']')[0]
                    comments_text = line.strip('[DhtmlXQ_comment').split('[')[0].split(']')[1]
                    if '_' in comments_info:
                        step_id = int(comments_info.split('_')[0])
                        step_index = int(comments_info.split('_')[1])
                        comments[(step_id, step_index)] = comments_text
                    else:
                        step_id = 0
                        step_index = int(comments_info)
                        comments[(step_id, step_index)] = comments_text
            for temp_step_index in range(len(temp_step_indexes)):
                target_step_id = temp_step_index + 1
                up_step_id, start_index, t_step = temp_step_indexes[target_step_id]
                target_step = steps[up_step_id][0][:(start_index - 1) * 4] + t_step
                steps[target_step_id] = [target_step, up_step_id, start_index]

        else:
            digitals = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
                        '１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9,
                        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}
            sub_steps = []
            for line in lines:
                if "." not in line:
                    continue
                # 解析棋步
                for j in range(len(line)):
                    step = line[j:j + 4]
                    if len(step) < 4:
                        break
                    elif step[2] in ['平', '进', '退'] and step[-1] in digitals:
                        sub_steps.append(step)

            steps[0] = sub_steps

        return steps, comments
