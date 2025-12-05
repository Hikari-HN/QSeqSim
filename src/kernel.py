from math import ceil, log2, sqrt, pi, isclose
import cmath as cm
from dd import cudd as _bdd
from fractions import Fraction
from decimal import Decimal, getcontext  # <--- 必须引入 decimal

# 设置 Decimal 的精度。
# 256 比特大约需要 77 位十进制精度。
# 为了安全处理中间运算和抵消，我们设置为 150 位。
getcontext().prec = 150 

class BDDCombSim:
    def __init__(self, n, r):
        self.BDD = _bdd.BDD()
        self.BDD.configure(reordering=True)
        self.n = n
        self.r = r
        for i in range(self.n):
            self.BDD.add_var('q%d' % i)
        self.Fa = []
        self.Fb = []
        self.Fc = []
        self.Fd = []
        for i in range(self.r):
            self.Fa.append(self.BDD.false)
            self.Fb.append(self.BDD.false)
            self.Fc.append(self.BDD.false)
            self.Fd.append(self.BDD.false)
        self.k = 0

    def init_basis_state(self, basis):
        assert basis < (1 << self.n), "Basis state is out of range!"
        tmp = dict()
        for i in range(self.n):
            tmp['q%d' % i] = bool((basis >> (self.n - 1 - i)) & 1)
        self.Fd[0] = self.BDD.cube(tmp)

    def Car(self, A, B, C):
        return self.BDD.add_expr(r'({A} & {B}) | (({A} | {B}) & {C})'.format(A=A, B=B, C=C))

    def Sum(self, A, B, C):
        return self.BDD.add_expr(r'{A} ^ {B} ^ {C}'.format(A=A, B=B, C=C))

    def X(self, target):
        r = len(self.Fd)
        trans = lambda x: (self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.false}, x)) | (
                ~self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.true}, x))
        for i in range(r):
            self.Fa[i] = trans(self.Fa[i])
            self.Fb[i] = trans(self.Fb[i])
            self.Fc[i] = trans(self.Fc[i])
            self.Fd[i] = trans(self.Fd[i])
        self.simplify_tail()

    def Y(self, target):
        r = len(self.Fd)
        g = lambda x: (self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.false}, x)) | (
                ~self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.true}, x))
        d1 = lambda x: (self.BDD.var('q%d' % target) & x) | (~self.BDD.var('q%d' % target) & ~x)
        d2 = lambda x: (self.BDD.var('q%d' % target) & ~x) | (~self.BDD.var('q%d' % target) & x)

        def trans1(x):
            Cx = []
            Cx.append(~self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Dx = d1(g(x[i]))
                Cx.append(self.Car(Dx, self.BDD.false, Cx[i]))
                tmpx.append(self.Sum(Dx, self.BDD.false, Cx[i]))
            tmpx.append(self.Sum(d1(g(x[r - 1])), self.BDD.false, Cx[r]))
            return tmpx.copy()

        def trans2(x):
            Cx = []
            Cx.append(self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Dx = d2(g(x[i]))
                Cx.append(self.Car(Dx, self.BDD.false, Cx[i]))
                tmpx.append(self.Sum(Dx, self.BDD.false, Cx[i]))
            tmpx.append(self.Sum(d2(g(x[r - 1])), self.BDD.false, Cx[r]))
            return tmpx.copy()

        tmpa = trans1(self.Fc)
        tmpb = trans1(self.Fd)
        tmpc = trans2(self.Fa)
        tmpd = trans2(self.Fb)
        self.Fa = tmpa.copy()
        self.Fb = tmpb.copy()
        self.Fc = tmpc.copy()
        self.Fd = tmpd.copy()
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

    def Z(self, target):
        r = len(self.Fd)
        g = lambda x: (~self.BDD.var('q%d' % target) & x) | (self.BDD.var('q%d' % target) & ~x)

        def trans(x):
            Cx = []
            Cx.append(self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Gx = g(x[i])
                Cx.append(self.Car(Gx, self.BDD.false, Cx[i]))
                tmpx.append(self.Sum(Gx, self.BDD.false, Cx[i]))
            tmpx.append(self.Sum(g(x[r - 1]), self.BDD.false, Cx[r]))
            return tmpx.copy()

        self.Fa = trans(self.Fa)
        self.Fb = trans(self.Fb)
        self.Fc = trans(self.Fc)
        self.Fd = trans(self.Fd)
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

    def H(self, target):
        r = len(self.Fd)
        g = lambda x: self.BDD.let({'q%d' % target: self.BDD.false}, x)
        d = lambda x: (~self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.true}, x)) | (
                self.BDD.var('q%d' % target) & ~x)

        def trans(x):
            Cx = []
            Cx.append(self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Gx = g(x[i])
                Dx = d(x[i])
                Cx.append(self.Car(Gx, Dx, Cx[i]))
                tmpx.append(self.Sum(Gx, Dx, Cx[i]))
            tmpx.append(self.Sum(g(x[r - 1]), d(x[r - 1]), Cx[r]))
            return tmpx.copy()

        self.Fa = trans(self.Fa)
        self.Fb = trans(self.Fb)
        self.Fc = trans(self.Fc)
        self.Fd = trans(self.Fd)
        self.k += 1
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

    def S(self, target):
        r = len(self.Fd)
        trans1 = lambda x, y: (~self.BDD.var('q%d' % target) & x) | (self.BDD.var('q%d' % target) & y)
        g = lambda x, y: (~self.BDD.var('q%d' % target) & x) | (self.BDD.var('q%d' % target) & ~y)
        tmpa = []
        tmpb = []
        for i in range(r):
            tmpa.append(trans1(self.Fa[i], self.Fc[i]))
            tmpb.append(trans1(self.Fb[i], self.Fd[i]))
        tmpa.append(tmpa[-1])
        tmpb.append(tmpb[-1])

        def trans2(x, y):
            Cx = []
            Cx.append(self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Gx = g(x[i], y[i])
                Cx.append(self.Car(Gx, self.BDD.false, Cx[i]))
                tmpx.append(self.Sum(Gx, self.BDD.false, Cx[i]))
            tmpx.append(self.Sum(g(x[r - 1], y[r - 1]), self.BDD.false, Cx[r]))
            return tmpx.copy()

        self.Fc = trans2(self.Fc, self.Fa)
        self.Fd = trans2(self.Fd, self.Fb)
        self.Fa = tmpa.copy()
        self.Fb = tmpb.copy()
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

    def T(self, target):
        r = len(self.Fd)
        trans1 = lambda x, y: (~self.BDD.var('q%d' % target) & x) | (self.BDD.var('q%d' % target) & y)
        g = lambda x, y: (~self.BDD.var('q%d' % target) & x) | (self.BDD.var('q%d' % target) & ~y)
        tmpa = []
        tmpb = []
        tmpc = []
        for i in range(r):
            tmpa.append(trans1(self.Fa[i], self.Fb[i]))
            tmpb.append(trans1(self.Fb[i], self.Fc[i]))
            tmpc.append(trans1(self.Fc[i], self.Fd[i]))
        tmpa.append(tmpa[-1])
        tmpb.append(tmpb[-1])
        tmpc.append(tmpc[-1])
        Cd = []
        Cd.append(self.BDD.var('q%d' % target))
        tmpd = []
        for i in range(r):
            Gd = g(self.Fd[i], self.Fa[i])
            Cd.append(self.Car(Gd, self.BDD.false, Cd[i]))
            tmpd.append(self.Sum(Gd, self.BDD.false, Cd[i]))
        tmpd.append(self.Sum(g(self.Fd[r - 1], self.Fa[r - 1]), self.BDD.false, Cd[r]))
        self.Fa = tmpa.copy()
        self.Fb = tmpb.copy()
        self.Fc = tmpc.copy()
        self.Fd = tmpd.copy()
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

    def TDG(self, target):
        self.Z(target)
        self.S(target)
        self.T(target)

    def SDG(self, target):
        self.Z(target)
        self.S(target)

    def X2P(self, target):
        # Rx(pi/2) gate
        r = len(self.Fd)
        d = lambda x: (self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.false}, x)) | (
                ~self.BDD.var('q%d' % target) & self.BDD.let({'q%d' % target: self.BDD.true}, x))

        def trans1(x, y):
            Cx = []
            Cx.append(self.BDD.true)
            tmpx = []
            for i in range(r):
                Dx = d(x[i])
                Cx.append(self.Car(y[i], ~Dx, Cx[i]))
                tmpx.append(self.Sum(y[i], ~Dx, Cx[i]))
            tmpx.append(self.Sum(y[r - 1], ~d(x[r - 1]), Cx[r]))
            return tmpx.copy()

        def trans2(x, y):
            Cx = []
            Cx.append(self.BDD.false)
            tmpx = []
            for i in range(r):
                Dx = d(x[i])
                Cx.append(self.Car(y[i], Dx, Cx[i]))
                tmpx.append(self.Sum(y[i], Dx, Cx[i]))
            tmpx.append(self.Sum(y[r - 1], d(x[r - 1]), Cx[r]))
            return tmpx.copy()

        tmpa = trans1(self.Fc, self.Fa)
        tmpb = trans1(self.Fd, self.Fb)
        tmpc = trans2(self.Fa, self.Fc)
        tmpd = trans2(self.Fb, self.Fd)
        self.Fa = tmpa.copy()
        self.Fb = tmpb.copy()
        self.Fc = tmpc.copy()
        self.Fd = tmpd.copy()
        self.k += 1
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

    def Y2P(self, target):
        # Ry(pi/2) gate
        r = len(self.Fd)
        g = lambda x: self.BDD.let({'q%d' % target: self.BDD.false}, x)
        d = lambda x: (self.BDD.var('q%d' % target) & x) | (
                ~self.BDD.var('q%d' % target) & ~self.BDD.let({'q%d' % target: self.BDD.true}, x))

        def trans(x):
            Cx = []
            Cx.append(~self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Gx = g(x[i])
                Dx = d(x[i])
                Cx.append(self.Car(Gx, Dx, Cx[i]))
                tmpx.append(self.Sum(Gx, Dx, Cx[i]))
            tmpx.append(self.Sum(g(x[r - 1]), d(x[r - 1]), Cx[r]))
            return tmpx.copy()

        self.Fa = trans(self.Fa)
        self.Fb = trans(self.Fb)
        self.Fc = trans(self.Fc)
        self.Fd = trans(self.Fd)
        self.k += 1
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

    def CNOT(self, control, target):
        r = len(self.Fd)

        def trans(x):
            return (~self.BDD.var('q%d' % control) & x) | (
                    self.BDD.var('q%d' % control) & self.BDD.var('q%d' % target) & self.BDD.let(
                {'q%d' % control: self.BDD.true, 'q%d' % target: self.BDD.false}, x)) | (
                    self.BDD.var('q%d' % control) & ~self.BDD.var('q%d' % target) & self.BDD.let(
                {'q%d' % control: self.BDD.true, 'q%d' % target: self.BDD.true}, x))

        for i in range(r):
            self.Fa[i] = trans(self.Fa[i])
            self.Fb[i] = trans(self.Fb[i])
            self.Fc[i] = trans(self.Fc[i])
            self.Fd[i] = trans(self.Fd[i])
        self.simplify_tail()

    def SWAP(self, target1, target2):
        self.CNOT(target1, target2)
        self.CNOT(target2, target1)
        self.CNOT(target1, target2)

    def CZ(self, control, target):
        r = len(self.Fd)
        g = lambda x: (~(self.BDD.var('q%d' % control) & self.BDD.var('q%d' % target)) & x) | (
                self.BDD.var('q%d' % control) & self.BDD.var('q%d' % target) & ~x)

        def trans(x):
            Cx = []
            Cx.append(self.BDD.var('q%d' % control) & self.BDD.var('q%d' % target))
            tmpx = []
            for i in range(r):
                Gx = g(x[i])
                Cx.append(self.Car(Gx, self.BDD.false, Cx[i]))
                tmpx.append(self.Sum(Gx, self.BDD.false, Cx[i]))
            tmpx.append(self.Sum(g(x[r - 1]), self.BDD.false, Cx[r]))
            return tmpx.copy()

        self.Fa = trans(self.Fa)
        self.Fb = trans(self.Fb)
        self.Fc = trans(self.Fc)
        self.Fd = trans(self.Fd)
        self.simplify_overflow()  # Overflow
        self.simplify_tail()

    def Toffoli(self, control1, control2, target):
        # CCNOT gate
        r = len(self.Fd)

        def trans(x):
            return (~(self.BDD.var('q%d' % control1) & self.BDD.var('q%d' % control2)) & x) | (
                    self.BDD.var('q%d' % control1) & self.BDD.var('q%d' % control2) & self.BDD.var(
                'q%d' % target) & self.BDD.let(
                {'q%d' % control1: self.BDD.true, 'q%d' % control2: self.BDD.true, 'q%d' % target: self.BDD.false},
                x)) | (self.BDD.var('q%d' % control1) & self.BDD.var('q%d' % control2) & ~self.BDD.var(
                'q%d' % target) & self.BDD.let(
                {'q%d' % control1: self.BDD.true, 'q%d' % control2: self.BDD.true, 'q%d' % target: self.BDD.true}, x))

        for i in range(r):
            self.Fa[i] = trans(self.Fa[i])
            self.Fb[i] = trans(self.Fb[i])
            self.Fc[i] = trans(self.Fc[i])
            self.Fd[i] = trans(self.Fd[i])
        self.simplify_tail()

    def Fredkin(self, control, target1, target2):
        # CSWAP gate
        r = len(self.Fd)

        def trans(x):
            return (~(self.BDD.var('q%d' % control) & self.BDD.apply('^', self.BDD.var('q%d' % target1),
                                                                     self.BDD.var('q%d' % target2))) & x) | (
                    self.BDD.var('q%d' % control) & self.BDD.var('q%d' % target1) & ~self.BDD.var(
                'q%d' % target2) & self.BDD.let(
                {'q%d' % control: self.BDD.true, 'q%d' % target1: self.BDD.false, 'q%d' % target2: self.BDD.true},
                x)) | (
                    self.BDD.var('q%d' % control) & ~self.BDD.var('q%d' % target1) & self.BDD.var(
                'q%d' % target2) & self.BDD.let(
                {'q%d' % control: self.BDD.true, 'q%d' % target1: self.BDD.true, 'q%d' % target2: self.BDD.false}, x))

        for i in range(r):
            self.Fa[i] = trans(self.Fa[i])
            self.Fb[i] = trans(self.Fb[i])
            self.Fc[i] = trans(self.Fc[i])
            self.Fd[i] = trans(self.Fd[i])
        self.simplify_tail()

    def cwalk(self, control, targets):
        self.X(control)
        for i in range(len(targets)):
            self.multi_controlled_X([control]+targets[i+1:], targets[i])
        self.X(control)
        for i in range(len(targets)-1, -1, -1):
            self.multi_controlled_X([control]+targets[i+1:], targets[i])
    def multi_controlled_X(self, controls, target):
        """
        实现 C^nX 门：当所有控制位均为 1 时，对目标位执行 X 翻转。
        controls: list or tuple, 存放控制位索引，比如 [c1, c2, ... , cn]
        target:  int，目标位索引
        """
        r = len(self.Fd)  # 假设和你已有代码风格一致

        def trans(x):
            # 1) 先构造 "all_controls" 表示所有控制位的与
            all_ctrl_expr = self.BDD.true
            for c in controls:
                all_ctrl_expr &= self.BDD.var('q%d' % c)

            # 2) 如果所有控制位都为 1，则执行翻转逻辑；否则不变
            #    翻转逻辑和 X 类似，需要区分目标位是 0 还是 1 后去做 let 替换
            return (
                    (~all_ctrl_expr & x) |
                    (all_ctrl_expr & self.BDD.var('q%d' % target) &
                     self.BDD.let(
                         {**{'q%d' % c: self.BDD.true for c in controls},
                          'q%d' % target: self.BDD.false},
                         x
                     )) |
                    (all_ctrl_expr & ~self.BDD.var('q%d' % target) &
                     self.BDD.let(
                         {**{'q%d' % c: self.BDD.true for c in controls},
                          'q%d' % target: self.BDD.true},
                         x
                     ))
            )

        # 3) 遍历更新 self.Fa / self.Fb / self.Fc / self.Fd
        for i in range(r):
            self.Fa[i] = trans(self.Fa[i])
            self.Fb[i] = trans(self.Fb[i])
            self.Fc[i] = trans(self.Fc[i])
            self.Fd[i] = trans(self.Fd[i])

        # 4) 末尾做一次化简，和你代码保持一致
        self.simplify_tail()

    # def get_total_bdd(self):
    #     m = ceil(log2(self.r)) + 2  # The number of index Boolean variables
    #     for i in range(m):
    #         self.BDD.add_var('x%d' % i)
    #     g = []
    #     for i in range(self.r):
    #         tmp = dict()
    #         for j in range(2, m):
    #             tmp['x%d' % j] = bool((i >> (j - 2)) & 1)
    #         g.append(self.BDD.cube(tmp))
    #     FA = self.BDD.false
    #     FB = self.BDD.false
    #     FC = self.BDD.false
    #     FD = self.BDD.false
    #     for i in range(self.r):
    #         FA = self.BDD.apply('|', FA, g[i] & self.Fa[i])
    #         FB = self.BDD.apply('|', FB, g[i] & self.Fb[i])
    #         FC = self.BDD.apply('|', FC, g[i] & self.Fc[i])
    #         FD = self.BDD.apply('|', FD, g[i] & self.Fd[i])
    #     x0 = self.BDD.var('x0')
    #     x1 = self.BDD.var('x1')
    #     return (x0 & x1 & FA) | (x0 & ~x1 & FB) | (~x0 & x1 & FC) | (~x0 & ~x1 & FD)

    # def get_prob(self, target_list, result_list):
    #     """
    #     target_list: the list of target qubits. NOTICE: Elements in a list cannot be the same!
    #     result_list: the list of measurement results.
    #     """
    #     if len(target_list) > len(result_list):
    #         target_list = target_list[:len(result_list)]
    #     if len(target_list) < self.n:
    #         next_list = self.get_next_list(target_list)
    #         return self.get_prob(next_list, result_list + [0]) + self.get_prob(next_list, result_list + [1])

    #     F = self.get_total_bdd()
    #     bool_list = [self.BDD.false, self.BDD.true]
    #     for i in range(len(target_list)):
    #         F = self.BDD.let({'q%d' % target_list[i]: bool_list[result_list[i]]}, F)
    #     FA = self.BDD.let({'x0': self.BDD.true, 'x1': self.BDD.true}, F)
    #     FB = self.BDD.let({'x0': self.BDD.true, 'x1': self.BDD.false}, F)
    #     FC = self.BDD.let({'x0': self.BDD.false, 'x1': self.BDD.true}, F)
    #     FD = self.BDD.let({'x0': self.BDD.false, 'x1': self.BDD.false}, F)
    #     a = self.get_value(FA)
    #     b = self.get_value(FB)
    #     c = self.get_value(FC)
    #     d = self.get_value(FD)
    #     w = cm.exp(1j * pi / 4)
    #     amplitude = (a * w ** 3 + b * w ** 2 + c * w + d) / pow(sqrt(2), self.k)
    #     return abs(amplitude) ** 2

    # def get_amplitude(self, cpt_basis):
    #     F = self.get_total_bdd()
    #     bool_list = [self.BDD.false, self.BDD.true]
    #     tmp = dict()
    #     for i in range(self.n):
    #         tmp['q%d' % i] = bool_list[(cpt_basis >> (self.n - 1 - i)) & 1]
    #     F = self.BDD.let(tmp, F)
    #     FA = self.BDD.let({'x0': self.BDD.true, 'x1': self.BDD.true}, F)
    #     FB = self.BDD.let({'x0': self.BDD.true, 'x1': self.BDD.false}, F)
    #     FC = self.BDD.let({'x0': self.BDD.false, 'x1': self.BDD.true}, F)
    #     FD = self.BDD.let({'x0': self.BDD.false, 'x1': self.BDD.false}, F)
    #     a = self.get_value(FA)
    #     b = self.get_value(FB)
    #     c = self.get_value(FC)
    #     d = self.get_value(FD)
    #     w = cm.exp(1j * pi / 4)
    #     amplitude = (a * w ** 3 + b * w ** 2 + c * w + d) / pow(sqrt(2), self.k)
    #     return amplitude

    def get_amplitude(self, cpt_basis):
        """
        【优化后的 get_amplitude】
        直接根据基态对 Fa/Fb/Fc/Fd 进行约束，不再构建巨大的 get_total_bdd。
        解决了内存爆炸问题。
        """
        # 1. 将整数基态 (如 5 -> 101) 转换为 BDD 的约束字典
        # 例如：{'q0': True, 'q1': False, 'q2': True}
        bool_list = [self.BDD.false, self.BDD.true]
        constraint_dict = dict()
        for i in range(self.n):
            # 注意：这里保持了你原代码的高位在前的逻辑
            bit_val = (cpt_basis >> (self.n - 1 - i)) & 1
            constraint_dict['q%d' % i] = bool_list[bit_val]

        # 2. 关键步骤：直接对四个分量列表应用约束
        # 因为 cpt_basis 包含所有量子比特，应用 let 后，
        # 列表中的每个 BDD 节点都会直接变成 True 或 False 常数节点。
        restricted_Fa = [self.BDD.let(constraint_dict, f) for f in self.Fa]
        restricted_Fb = [self.BDD.let(constraint_dict, f) for f in self.Fb]
        restricted_Fc = [self.BDD.let(constraint_dict, f) for f in self.Fc]
        restricted_Fd = [self.BDD.let(constraint_dict, f) for f in self.Fd]

        # 3. 直接计算整数值
        val_a = self._get_value_from_list(restricted_Fa)
        val_b = self._get_value_from_list(restricted_Fb)
        val_c = self._get_value_from_list(restricted_Fc)
        val_d = self._get_value_from_list(restricted_Fd)

        # 4. 组合复数幅值
        w = cm.exp(1j * pi / 4)
        amplitude = (val_a * w ** 3 + val_b * w ** 2 + val_c * w + val_d) / pow(sqrt(2), self.k)

        return amplitude


    def mid_measure(self, target_list, result_list):
        l = len(result_list)
        d = {'q%d' % target_list[j]: bool(result_list[j]) for j in range(l)}
        constraint = self.BDD.true
        for j in range(l):
            var = self.BDD.var('q%d' % target_list[j])
            if result_list[j]:
                constraint &= var
            else:
                constraint &= ~var
        for i in range(self.r):
            # Apply substitution using let
            self.Fa[i] = self.BDD.let(d, self.Fa[i]) & constraint
            self.Fb[i] = self.BDD.let(d, self.Fb[i]) & constraint
            self.Fc[i] = self.BDD.let(d, self.Fc[i]) & constraint
            self.Fd[i] = self.BDD.let(d, self.Fd[i]) & constraint
        self.simplify_tail()

    def reset(self, target):
        r = len(self.Fd)
        trans = lambda x: (~self.BDD.var('q%d' % target)) & (self.BDD.let({'q%d' % target: self.BDD.false}, x) |
                                                             self.BDD.let({'q%d' % target: self.BDD.true}, x))
        for i in range(r):
            self.Fa[i] = trans(self.Fa[i])
            self.Fb[i] = trans(self.Fb[i])
            self.Fc[i] = trans(self.Fc[i])
            self.Fd[i] = trans(self.Fd[i])
        self.simplify_tail()

    def measure(self, target_list, result_list):
        tmp = target_list.copy()
        print("The probability of measuring qubits %s and getting results %s is %f." % (
            target_list, result_list, self.get_prob(tmp, result_list)))

    def get_next_list(self, target_list):
        for i in range(self.n):
            if i not in target_list:
                target_list.append(i)
                break
        return target_list

    # def get_value(self, bdd):
    #     m = ceil(log2(self.r)) + 2  # The number of index Boolean variables
    #     bool_list = [self.BDD.false, self.BDD.true]
    #     binary_list = []
    #     for i in range(self.r):
    #         tmp = dict()
    #         for j in range(2, m):
    #             tmp['x%d' % j] = bool_list[(i >> (j - 2)) & 1]
    #         flag = self.BDD.let(tmp, bdd)
    #         if flag == self.BDD.true:
    #             binary_list.append(1)
    #         else:
    #             binary_list.append(0)
    #     if binary_list[-1] == 0:
    #         return sum([(1 << i) if binary_list[i] == 1 else 0 for i in range(len(binary_list) - 1)])
    #     else:
    #         return -sum([(1 << i) if binary_list[i] == 0 else 0 for i in range(len(binary_list) - 1)]) - 1
        
    # def get_prob(self, target_list, result_list):
    #     """
    #     优化后的概率计算：先对分量 BDD 进行约束，再计算幅值。
    #     避免构建巨大的 get_total_bdd。
    #     """
    #     # 1. 处理 target_list 和 result_list 的长度匹配
    #     if len(target_list) > len(result_list):
    #         target_list = target_list[:len(result_list)]
        
    #     # 2. 如果测量的不是所有量子比特，需要递归求和 (边缘概率)
    #     # 注意：这一步在深层递归时仍然可能慢，但在全测量或大部分测量时会快很多
    #     if len(target_list) < self.n:
    #         next_list = self.get_next_list(target_list)
    #         # 递归分支：分别计算测量为0和1的概率并相加
    #         return self.get_prob(next_list, result_list + [0]) + \
    #                self.get_prob(next_list, result_list + [1])

    #     # 3. 构造约束字典 (Restriction Dictionary)
    #     # 将测量结果转化为 BDD 的 let 字典
    #     bool_list = [self.BDD.false, self.BDD.true]
    #     constraint_dict = {}
    #     for i in range(len(target_list)):
    #         constraint_dict['q%d' % target_list[i]] = bool_list[result_list[i]]

    #     # 4. 【关键优化步骤】：先对 Fa, Fb, Fc, Fd 进行约束 (Let)
    #     # 这会使得 BDD 规模急剧减小，甚至变成常数节点
    #     restricted_Fa = [self.BDD.let(constraint_dict, f) for f in self.Fa]
    #     restricted_Fb = [self.BDD.let(constraint_dict, f) for f in self.Fb]
    #     restricted_Fc = [self.BDD.let(constraint_dict, f) for f in self.Fc]
    #     restricted_Fd = [self.BDD.let(constraint_dict, f) for f in self.Fd]

    #     # 5. 基于约束后的 BDD 计算复数幅值
    #     # 我们不再需要构建完整的 get_total_bdd，而是直接计算这四个分量的加权和
        
    #     # 计算四个分量的整数值
    #     val_a = self._get_value_from_list(restricted_Fa)
    #     val_b = self._get_value_from_list(restricted_Fb)
    #     val_c = self._get_value_from_list(restricted_Fc)
    #     val_d = self._get_value_from_list(restricted_Fd)

    #     # 6. 组合复数幅值
    #     w = cm.exp(1j * pi / 4)
    #     amplitude = (val_a * w ** 3 + val_b * w ** 2 + val_c * w + val_d) / pow(sqrt(2), self.k)
        
    #     return abs(amplitude) ** 2
    def _get_value_from_assignment(self, bdd_list, assignment):
        """
        辅助函数：给定一个具体的变量赋值 (assignment)，计算 bdd_list 代表的整数值。
        """
        # 计算符号位
        is_negative = (self.BDD.let(assignment, bdd_list[-1]) == self.BDD.true)
        
        final_val = 0
        limit = self.r - 1
        
        if not is_negative:
            for i in range(limit):
                # 对每一位 BDD 应用赋值，看结果是 True 还是 False
                if self.BDD.let(assignment, bdd_list[i]) == self.BDD.true:
                    final_val += (1 << i)
            return final_val
        else:
            for i in range(limit):
                if self.BDD.let(assignment, bdd_list[i]) == self.BDD.false:
                    final_val += (1 << i)
            return -final_val - 1

    # ----------------- 终极优化版 get_prob -----------------

    # def get_prob(self, target_list, result_list):
    #     """
    #     通用型概率计算：使用符号化计数 (Symbolic Counting)。
    #     既适用于稀疏态 (Random Walk)，也适用于稠密态 (Grover)。
    #     不再依赖路径枚举，而是直接计算 BDD 图的加权节点数。
    #     """
    #     # 1. 构造约束
    #     bool_list = [self.BDD.false, self.BDD.true]
    #     constraint_dict = {}
    #     for t, r in zip(target_list, result_list):
    #         constraint_dict['q%d' % t] = bool_list[r]

    #     # 2. 施加约束 (Let) - 这一步极快
    #     res_Fa = [self.BDD.let(constraint_dict, f) for f in self.Fa]
    #     res_Fb = [self.BDD.let(constraint_dict, f) for f in self.Fb]
    #     res_Fc = [self.BDD.let(constraint_dict, f) for f in self.Fc]
    #     res_Fd = [self.BDD.let(constraint_dict, f) for f in self.Fd]

    #     # 3. 确定需要计数的变量集合 (未测量的量子比特)
    #     all_qubits = set(range(self.n))
    #     measured_qubits = set(target_list)
    #     unmeasured_indices = list(all_qubits - measured_qubits)
    #     # 注意：dd 的 count 需要知道变量总数或具体的变量集
    #     # 这里我们只关心未测量的变量，它们构成了剩余的希尔伯特空间
    #     n_vars = len(unmeasured_indices) 
        
    #     # 如果所有比特都被测量了，直接计算单值
    #     if n_vars == 0:
    #         val_a = self._get_value_from_list(res_Fa)
    #         val_b = self._get_value_from_list(res_Fb)
    #         val_c = self._get_value_from_list(res_Fc)
    #         val_d = self._get_value_from_list(res_Fd)
    #         w = cm.exp(1j * pi / 4)
    #         amp = (val_a * w ** 3 + val_b * w ** 2 + val_c * w + val_d) / pow(sqrt(2), self.k)
    #         return abs(amp) ** 2

    #     # 4. 核心：符号化计算模长平方
    #     # 我们需要计算 sum(|Amp|^2) over all x
    #     # Amp = (A*w^3 + B*w^2 + C*w + D) / sqrt(2)^k
    #     # |Amp|^2 = A^2 + B^2 + C^2 + D^2 + sqrt(2)*(AB + BC + CD - AD)
    #     # (注：AC 和 BD 项系数为 0)
        
    #     # 计算各项的内积 (Inner Product)
    #     # dot(A, A) 表示 sum(A(x)^2)
    #     aa = self._symbolic_inner_product(res_Fa, res_Fa, n_vars)
    #     bb = self._symbolic_inner_product(res_Fb, res_Fb, n_vars)
    #     cc = self._symbolic_inner_product(res_Fc, res_Fc, n_vars)
    #     dd = self._symbolic_inner_product(res_Fd, res_Fd, n_vars)
        
    #     ab = self._symbolic_inner_product(res_Fa, res_Fb, n_vars)
    #     bc = self._symbolic_inner_product(res_Fb, res_Fc, n_vars)
    #     cd = self._symbolic_inner_product(res_Fc, res_Fd, n_vars)
    #     ad = self._symbolic_inner_product(res_Fa, res_Fd, n_vars)

    #     # 组合结果
    #     # sum_sq = A^2 + B^2 + C^2 + D^2 + sqrt(2)*(AB + BC + CD - AD)
    #     total_sum = aa + bb + cc + dd + sqrt(2) * (ab + bc + cd - ad)
        
    #     return total_sum / (pow(2, self.k))
    
    def get_prob(self, target_list, result_list):
        """
        旗舰版概率计算：支持 256+ 量子比特。
        1. 使用整数平方判别法进行【精确零检测】，彻底消除噪声。
        2. 使用 Decimal 进行【高精度计算】，保留 10^-78 级别的微小概率。
        """
        # 1. 构造约束 & 2. 施加约束 (保持不变)
        bool_list = [self.BDD.false, self.BDD.true]
        constraint_dict = {}
        for t, r in zip(target_list, result_list):
            constraint_dict['q%d' % t] = bool_list[r]

        res_Fa = [self.BDD.let(constraint_dict, f) for f in self.Fa]
        res_Fb = [self.BDD.let(constraint_dict, f) for f in self.Fb]
        res_Fc = [self.BDD.let(constraint_dict, f) for f in self.Fc]
        res_Fd = [self.BDD.let(constraint_dict, f) for f in self.Fd]

        # 3. 确定未测量的变量 (保持不变)
        all_qubits = set(range(self.n))
        measured_qubits = set(target_list)
        unmeasured_indices = list(all_qubits - measured_qubits)
        n_vars = len(unmeasured_indices) 
        
        # 4. 符号化计算模长平方的各个项 (保持不变)
        # 这里返回的都是 Python 的大整数，精度无限，不会溢出
        aa = self._symbolic_inner_product(res_Fa, res_Fa, n_vars)
        bb = self._symbolic_inner_product(res_Fb, res_Fb, n_vars)
        cc = self._symbolic_inner_product(res_Fc, res_Fc, n_vars)
        dd = self._symbolic_inner_product(res_Fd, res_Fd, n_vars)
        
        ab = self._symbolic_inner_product(res_Fa, res_Fb, n_vars)
        bc = self._symbolic_inner_product(res_Fb, res_Fc, n_vars)
        cd = self._symbolic_inner_product(res_Fc, res_Fd, n_vars)
        ad = self._symbolic_inner_product(res_Fa, res_Fd, n_vars)

        # 5. 组合结果
        # Total = (term_int + sqrt(2) * term_sqrt) / 2^k
        term_int = aa + bb + cc + dd
        term_sqrt = ab + bc + cd - ad
        
        # =========================================================
        # 核心改进 A：精确零检测 (Exact Zero Check)
        # =========================================================
        # 我们想知道 term_int + sqrt(2)*term_sqrt 是否严格等于 0
        # 即判断 term_int 是否等于 -sqrt(2)*term_sqrt
        # 两边平方： term_int^2 == 2 * term_sqrt^2
        # 这是一个纯整数比较，没有任何误差！
        
        is_zero = False
        if term_int == 0 and term_sqrt == 0:
            is_zero = True
        elif (term_int * term_sqrt < 0) and (term_int**2 == 2 * (term_sqrt**2)):
            # 如果符号相反，且平方满足2倍关系，说明是精确抵消
            is_zero = True
            
        if is_zero:
            return 0.0

        # =========================================================
        # 核心改进 B：高精度计算 (Decimal)
        # =========================================================
        # 如果不是 0，我们需要计算它的值。
        # 对于 256 比特，结果约为 1e-78。
        # 普通 float 的精度不足以在 term_int 和 term_sqrt 很大时保留这个微小值。
        
        # 使用 Decimal 计算 sqrt(2)
        sqrt2_dec = Decimal(2).sqrt()
        
        # 分子
        numerator = Decimal(term_int) + sqrt2_dec * Decimal(term_sqrt)
        
        # 分母 2^k
        # 注意：self.k 对于 256 比特可能很大，直接用 1<<self.k 生成大整数
        divisor = Decimal(1 << self.k)
        
        # 高精度除法
        total_prob_dec = numerator / divisor
        
        # 最后转回 float 返回给用户
        # Python 的 float 可以表示 1e-308，所以 1e-78 是安全的
        # 只要计算过程用 Decimal 保证了精度，结果就是准确的
        return abs(float(total_prob_dec))
    
    # def get_prob(self, target_list, result_list):
    #     """
    #     通用型概率计算：使用符号化计数 + Fraction 高精度除法。
    #     修复了 Grover 算法中归一化因子过大导致的 OverflowError。
    #     """
    #     # 1. 构造约束
    #     bool_list = [self.BDD.false, self.BDD.true]
    #     constraint_dict = {}
    #     for t, r in zip(target_list, result_list):
    #         constraint_dict['q%d' % t] = bool_list[r]

    #     # 2. 施加约束 (Let)
    #     res_Fa = [self.BDD.let(constraint_dict, f) for f in self.Fa]
    #     res_Fb = [self.BDD.let(constraint_dict, f) for f in self.Fb]
    #     res_Fc = [self.BDD.let(constraint_dict, f) for f in self.Fc]
    #     res_Fd = [self.BDD.let(constraint_dict, f) for f in self.Fd]

    #     # 3. 确定未测量的变量
    #     all_qubits = set(range(self.n))
    #     measured_qubits = set(target_list)
    #     unmeasured_indices = list(all_qubits - measured_qubits)
    #     n_vars = len(unmeasured_indices) 
        
    #     # 4. 符号化计算模长平方的各个项
    #     aa = self._symbolic_inner_product(res_Fa, res_Fa, n_vars)
    #     bb = self._symbolic_inner_product(res_Fb, res_Fb, n_vars)
    #     cc = self._symbolic_inner_product(res_Fc, res_Fc, n_vars)
    #     dd = self._symbolic_inner_product(res_Fd, res_Fd, n_vars)
        
    #     ab = self._symbolic_inner_product(res_Fa, res_Fb, n_vars)
    #     bc = self._symbolic_inner_product(res_Fb, res_Fc, n_vars)
    #     cd = self._symbolic_inner_product(res_Fc, res_Fd, n_vars)
    #     ad = self._symbolic_inner_product(res_Fa, res_Fd, n_vars)

    #     # 5. 组合结果 (关键修复步骤)
    #     # 公式: Sum = (aa+bb+cc+dd) + sqrt(2)*(ab+bc+cd-ad)
    #     # 我们需要计算 Sum / 2^k
        
    #     term_int = aa + bb + cc + dd
    #     term_sqrt = ab + bc + cd - ad
    #     divisor = 1 << self.k  # 使用位移计算 2^k，比 pow 更快且保持整数
        
    #     # 使用 Fraction 进行安全的整数除法
    #     # Fraction(大整数, 大整数) 会自动约分，结果是一个有理数对象
    #     # 将其转为 float 时，因为结果是概率(<=1)，所以绝对不会溢出
    #     # 【修复点】强制转换为 int，确保传入 Fraction 的是整数
    #     prob_int_part = float(Fraction(int(term_int), int(divisor)))
    #     prob_sqrt_part = float(Fraction(int(term_sqrt), int(divisor)))
        
    #     total_prob = prob_int_part + sqrt(2) * prob_sqrt_part
        
    #     # 【新增】数值清洗：如果概率极小，视为 0
    #     # 1e-15 是双精度浮点数的安全误差界限
    #     if abs(total_prob) < 1e-15:
    #         return 0.0
        
    #     return abs(total_prob) # 确保非负

    def _symbolic_inner_product(self, list1, list2, n_vars):
        """
        计算两个整数向量 BDD 的内积。
        修复 NaN 问题：不再向 count 传递 nvars，而是手动计算缩放因子。
        """
        total = 0
        r = self.r
        
        # 预计算权重
        weights = []
        for i in range(r - 1):
            weights.append(1 << i)
        weights.append(-(1 << (r - 1))) 

        for i in range(r):
            for j in range(r):
                and_node = list1[i] & list2[j]
                
                # 如果交集为空，跳过
                if and_node == self.BDD.false:
                    continue
                
                # 1. 获取原始计数 (Raw Count)
                # 不传 nvars，让它只计算 BDD 实际依赖变量的满足路径数
                # count 返回 float，必须转 int
                raw_count = int(self.BDD.count(and_node))
                
                # 2. 获取支撑集大小 (Support Size)
                # support 返回该节点实际依赖的变量集合
                supp = self.BDD.support(and_node)
                len_supp = len(supp)
                
                # 3. 手动计算缩放因子 (Scaling)
                # n_vars 是我们逻辑上剩余的自由量子比特数
                # diff 是 BDD 没用到但实际存在的自由比特数，每一个贡献 2 倍的路径
                diff = n_vars - len_supp
                
                # 防御性处理：理论上 diff >= 0。如果 < 0 说明逻辑有误，保持原值
                shift = diff if diff > 0 else 0
                
                # 使用位移操作相当于乘以 2^shift
                real_count = raw_count << shift
                
                # 累加
                total += weights[i] * weights[j] * real_count
                    
        return total
    # def _symbolic_inner_product(self, list1, list2, n_vars):
    #     """
    #     计算两个整数向量 BDD 的内积：sum_{x} (Val1(x) * Val2(x))
    #     利用 count 函数避免遍历状态。
    #     """
    #     total = 0
    #     r = self.r
        
    #     # 预计算每一位的权重
    #     # 标准补码权重：第 i 位是 2^i，最高位(符号位)是 -2^(r-1)
    #     weights = []
    #     for i in range(r - 1):
    #         weights.append(1 << i)
    #     weights.append(-(1 << (r - 1))) # 符号位权重

    #     # 双重循环累加： sum( w_i * w_j * count(bit_i & bit_j) )
    #     # 这里的 count 是 C++ 级别的操作，非常快
    #     for i in range(r):
    #         for j in range(r):
    #             # 两个 BDD 的逻辑与
    #             and_node = list1[i] & list2[j]
                
    #             # 如果交集为 False，跳过
    #             if and_node == self.BDD.false:
    #                 continue
                
    #             # 统计满足条件的路径数
    #             # count 返回的是满足该 BDD 为 True 的赋值数量
    #             c = self.BDD.count(and_node, nvars=n_vars)
                
    #             if c > 0:
    #                 total += weights[i] * weights[j] * c
                    
    #     return total

    def _get_value_from_list(self, bdd_list):
        """
        【新增辅助函数】
        从已经坍缩（被let约束过）的 BDD 列表中直接计算整数值。
        替代了原有的 get_value 函数，不需要引入 x 变量，速度极快。
        """
        # 1. 判断符号位 (最高位)
        # 在你的逻辑中，最后一位是符号位：True代表负数，False代表正数
        is_negative = (bdd_list[-1] == self.BDD.true)

        final_val = 0
        
        # 2. 根据正负逻辑还原数值
        if not is_negative:
            # 正数逻辑：直接累加为 True 的位
            for i in range(self.r - 1):
                if bdd_list[i] == self.BDD.true:
                    final_val += (1 << i)
            return final_val
        else:
            # 负数逻辑：累加为 False (0) 的位，最后取反再减1
            # 对应原代码：-sum([(1 << i) if binary_list[i] == 0 ...]) - 1
            for i in range(self.r - 1):
                if bdd_list[i] == self.BDD.false: 
                    final_val += (1 << i)
            return -final_val - 1

    # ----------------- 优化结束 -----------------

    def simplify_tail(self):
        if self.Fa[0] == self.BDD.false and self.Fb[0] == self.BDD.false and self.Fc[0] == self.BDD.false and self.Fd[
            0] == self.BDD.false:
            self.Fa = self.Fa[1:]
            self.Fb = self.Fb[1:]
            self.Fc = self.Fc[1:]
            self.Fd = self.Fd[1:]
            self.k -= 2
        self.r = len(self.Fd)

    def simplify_overflow(self):
        if self.Fa[-1] == self.Fa[-2] and self.Fb[-1] == self.Fb[-2] and self.Fc[-1] == self.Fc[-2] and self.Fd[-1] == \
                self.Fd[-2]:
            self.Fa.pop()
            self.Fb.pop()
            self.Fc.pop()
            self.Fd.pop()

    def signed_extend(self, length):
        for i in range(length):
            self.Fa.append(self.Fa[-1])
            self.Fb.append(self.Fb[-1])
            self.Fc.append(self.Fc[-1])
            self.Fd.append(self.Fd[-1])
        self.r += length

    def print_bdd(self):
        """
            Only can be used when import autoref instead of cudd!
        """
        print("Fa:")
        for i in range(len(self.Fa)):
            print(self.Fa[i].to_expr())
        print("Fb:")
        for i in range(len(self.Fb)):
            print(self.Fb[i].to_expr())
        print("Fc:")
        for i in range(len(self.Fc)):
            print(self.Fc[i].to_expr())
        print("Fd:")
        for i in range(len(self.Fd)):
            print(self.Fd[i].to_expr())

    def print_state_vec(self):
        for i in range(1 << self.n):
            print("The amplitude of |%s> is" % bin(i)[2:].zfill(self.n), self.get_amplitude(i), end='.\n')


class BDDSeqSim:
    def __init__(self, n, m, r):
        """
            n represents the number of all qubits
            m represents the number of input qubits
        """
        self.comb_bdd = BDDCombSim(n, r)
        self.stored_bdd = BDDCombSim(m, r)
        self.input_bdd = BDDCombSim(n - m, r)
        self.n = n
        self.m = m
        self.r = r
        self.k = 0
        self.prob_list = []

    def init_stored_state_by_basis(self, basis):
        assert basis < (1 << self.m), "Basis state is out of range!"
        tmp = dict()
        for i in range(self.m):
            tmp['q%d' % i] = bool((basis >> (self.m - 1 - i)) & 1)
        self.stored_bdd.Fd[0] = self.stored_bdd.BDD.cube(tmp)

    def init_stored_state_by_bdd(self, bdd):
        self.stored_bdd = bdd

    def init_input_state_by_basis(self, basis):
        num = self.n - self.m
        assert basis < (1 << num), "Basis state is out of range!"
        tmp = dict()
        for i in range(num):
            tmp['q%d' % i] = bool((basis >> (num - 1 - i)) & 1)
        self.input_bdd.Fd[0] = self.input_bdd.BDD.cube(tmp)

    # def init_input_state_by_bdd(self, bdd):
    #     self.input_bdd = bdd

    def init_comb_bdd(self):
        """
            input_bdd and stored_bdd should be initialized before calling this function.
            comb_bdd is the tensor product of the input_bdd and stored_bdd.
        """
        # TODO: the case of different r needs to be tested, now they are always the same.
        if self.input_bdd.r > self.stored_bdd.r:
            self.stored_bdd.signed_extend(self.input_bdd.r - self.stored_bdd.r)
        elif self.input_bdd.r < self.stored_bdd.r:
            self.input_bdd.signed_extend(self.stored_bdd.r - self.input_bdd.r)
        self.comb_bdd = BDDCombSim(self.n, self.stored_bdd.r)

        def tensor(x, y):
            tmpx = self.input_bdd.BDD.copy(x, self.comb_bdd.BDD)
            tmpy = self.stored_bdd.BDD.copy(y, self.comb_bdd.BDD)
            tmpd = dict()
            for i in range(self.m):
                tmpd['q%d' % i] = 'q%d' % (i + self.n - self.m)
            tmpy = self.comb_bdd.BDD.let(tmpd, tmpy)
            return tmpx & tmpy

        for i in range(self.comb_bdd.r):
            # Because input_bdd is represented by a basis state, it only has Fd[0].
            self.comb_bdd.Fa[i] = tensor(self.input_bdd.Fd[0], self.stored_bdd.Fa[i])
            self.comb_bdd.Fb[i] = tensor(self.input_bdd.Fd[0], self.stored_bdd.Fb[i])
            self.comb_bdd.Fc[i] = tensor(self.input_bdd.Fd[0], self.stored_bdd.Fc[i])
            self.comb_bdd.Fd[i] = tensor(self.input_bdd.Fd[0], self.stored_bdd.Fd[i])
        self.comb_bdd.k = self.stored_bdd.k
        self.r = self.comb_bdd.r
        self.k = self.comb_bdd.k

    def X(self, target):
        self.comb_bdd.X(target)

    def Y(self, target):
        self.comb_bdd.Y(target)

    def Z(self, target):
        self.comb_bdd.Z(target)

    def H(self, target):
        self.comb_bdd.H(target)

    def S(self, target):
        self.comb_bdd.S(target)

    def T(self, target):
        self.comb_bdd.T(target)

    def X2P(self, target):
        self.comb_bdd.X2P(target)

    def Y2P(self, target):
        self.comb_bdd.Y2P(target)

    def CNOT(self, control, target):
        self.comb_bdd.CNOT(control, target)

    def SWAP(self, target1, target2):
        self.comb_bdd.SWAP(target1, target2)

    def CZ(self, control, target):
        self.comb_bdd.CZ(control, target)

    def Toffoli(self, control1, control2, target):
        self.comb_bdd.Toffoli(control1, control2, target)

    def Fredkin(self, control, target1, target2):
        self.comb_bdd.Fredkin(control, target1, target2)

    def cwalk(self, control, targets):
        self.comb_bdd.cwalk(control, targets)

    def multi_controlled_X(self, controls, target):
        self.comb_bdd.multi_controlled_X(controls, target)

    def mid_measure(self, target_list, result_list):
        self.comb_bdd.mid_measure(target_list, result_list)

    def reset(self, target):
        self.comb_bdd.reset(target)

    def measure(self, result_list):
        
        l = len(result_list)
        assert l == self.n - self.m, "The length of result list is wrong!"
        self.prob_list.append(self.comb_bdd.get_prob(list(range(l)), result_list))
        d = {'q%d' % j: bool(result_list[j]) for j in range(l)}
        for i in range(self.comb_bdd.r):
            self.comb_bdd.Fa[i] = self.comb_bdd.BDD.let(d, self.comb_bdd.Fa[i])
            self.comb_bdd.Fb[i] = self.comb_bdd.BDD.let(d, self.comb_bdd.Fb[i])
            self.comb_bdd.Fc[i] = self.comb_bdd.BDD.let(d, self.comb_bdd.Fc[i])
            self.comb_bdd.Fd[i] = self.comb_bdd.BDD.let(d, self.comb_bdd.Fd[i])
        self.comb_bdd.simplify_tail()
        self.stored_bdd = BDDCombSim(self.m, self.comb_bdd.r)
        self.stored_bdd.k = self.comb_bdd.k

        def update(x):
            tmpd = dict()
            for i in range(self.m):
                tmpd['q%d' % (i + self.n - self.m)] = 'q%d' % i
            x = self.comb_bdd.BDD.let(tmpd, x)
            return self.comb_bdd.BDD.copy(x, self.stored_bdd.BDD)

        for i in range(self.comb_bdd.r):
            self.stored_bdd.Fa[i] = update(self.comb_bdd.Fa[i])
            self.stored_bdd.Fb[i] = update(self.comb_bdd.Fb[i])
            self.stored_bdd.Fc[i] = update(self.comb_bdd.Fc[i])
            self.stored_bdd.Fd[i] = update(self.comb_bdd.Fd[i])

        self.r = self.stored_bdd.r
        self.k = self.stored_bdd.k

    def get_step_prob(self):
        if len(self.prob_list) == 1:
            return self.prob_list[-1]
        else:
            return self.prob_list[-1] / self.prob_list[-2]

    def print_stored_state_vec(self):
        for i in range(1 << self.m):
            print("The amplitude of |%s> is" % bin(i)[2:].zfill(self.m),
                  self.stored_bdd.get_amplitude(i) / sqrt(self.prob_list[-1]), end='.\n')
