# Generated from Lineage.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,18,41,2,0,7,0,2,1,7,1,2,2,7,2,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,
        0,3,0,15,8,0,1,0,1,0,1,0,1,0,1,0,1,0,5,0,23,8,0,10,0,12,0,26,9,0,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,2,1,2,1,2,1,2,0,1,0,3,
        0,2,4,0,3,1,0,1,2,1,0,3,4,1,0,7,12,42,0,14,1,0,0,0,2,27,1,0,0,0,
        4,36,1,0,0,0,6,7,6,0,-1,0,7,8,5,5,0,0,8,9,3,0,0,0,9,10,5,6,0,0,10,
        15,1,0,0,0,11,15,3,2,1,0,12,15,5,17,0,0,13,15,5,16,0,0,14,6,1,0,
        0,0,14,11,1,0,0,0,14,12,1,0,0,0,14,13,1,0,0,0,15,24,1,0,0,0,16,17,
        10,6,0,0,17,18,7,0,0,0,18,23,3,0,0,7,19,20,10,5,0,0,20,21,7,1,0,
        0,21,23,3,0,0,6,22,16,1,0,0,0,22,19,1,0,0,0,23,26,1,0,0,0,24,22,
        1,0,0,0,24,25,1,0,0,0,25,1,1,0,0,0,26,24,1,0,0,0,27,28,5,13,0,0,
        28,29,5,5,0,0,29,30,3,4,2,0,30,31,5,6,0,0,31,32,5,14,0,0,32,33,3,
        0,0,0,33,34,5,15,0,0,34,35,3,0,0,0,35,3,1,0,0,0,36,37,3,0,0,0,37,
        38,7,2,0,0,38,39,3,0,0,0,39,5,1,0,0,0,3,14,22,24
    ]

class LineageParser ( Parser ):

    grammarFileName = "Lineage.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'*'", "'/'", "'+'", "'-'", "'('", "')'", 
                     "'=='", "'!='", "'<'", "'<='", "'>'", "'>='", "'if'", 
                     "'then'", "'else'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "IF", "THEN", "ELSE", "NUMBER", "IDENTIFIER", 
                      "WS" ]

    RULE_expr = 0
    RULE_ifExpr = 1
    RULE_condition = 2

    ruleNames =  [ "expr", "ifExpr", "condition" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    IF=13
    THEN=14
    ELSE=15
    NUMBER=16
    IDENTIFIER=17
    WS=18

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return LineageParser.RULE_expr

     
        def copyFrom(self, ctx:ParserRuleContext):
            super().copyFrom(ctx)


    class MulDivContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LineageParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LineageParser.ExprContext)
            else:
                return self.getTypedRuleContext(LineageParser.ExprContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMulDiv" ):
                return visitor.visitMulDiv(self)
            else:
                return visitor.visitChildren(self)


    class AddSubContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LineageParser.ExprContext
            super().__init__(parser)
            self.op = None # Token
            self.copyFrom(ctx)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LineageParser.ExprContext)
            else:
                return self.getTypedRuleContext(LineageParser.ExprContext,i)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddSub" ):
                return visitor.visitAddSub(self)
            else:
                return visitor.visitChildren(self)


    class ParensContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LineageParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def expr(self):
            return self.getTypedRuleContext(LineageParser.ExprContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitParens" ):
                return visitor.visitParens(self)
            else:
                return visitor.visitChildren(self)


    class VarContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LineageParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def IDENTIFIER(self):
            return self.getToken(LineageParser.IDENTIFIER, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVar" ):
                return visitor.visitVar(self)
            else:
                return visitor.visitChildren(self)


    class ConstContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LineageParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def NUMBER(self):
            return self.getToken(LineageParser.NUMBER, 0)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitConst" ):
                return visitor.visitConst(self)
            else:
                return visitor.visitChildren(self)


    class IfElseExprContext(ExprContext):

        def __init__(self, parser, ctx:ParserRuleContext): # actually a LineageParser.ExprContext
            super().__init__(parser)
            self.copyFrom(ctx)

        def ifExpr(self):
            return self.getTypedRuleContext(LineageParser.IfExprContext,0)


        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIfElseExpr" ):
                return visitor.visitIfElseExpr(self)
            else:
                return visitor.visitChildren(self)



    def expr(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = LineageParser.ExprContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 0
        self.enterRecursionRule(localctx, 0, self.RULE_expr, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 14
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [5]:
                localctx = LineageParser.ParensContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx

                self.state = 7
                self.match(LineageParser.T__4)
                self.state = 8
                self.expr(0)
                self.state = 9
                self.match(LineageParser.T__5)
                pass
            elif token in [13]:
                localctx = LineageParser.IfElseExprContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 11
                self.ifExpr()
                pass
            elif token in [17]:
                localctx = LineageParser.VarContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 12
                self.match(LineageParser.IDENTIFIER)
                pass
            elif token in [16]:
                localctx = LineageParser.ConstContext(self, localctx)
                self._ctx = localctx
                _prevctx = localctx
                self.state = 13
                self.match(LineageParser.NUMBER)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 24
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,2,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 22
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
                    if la_ == 1:
                        localctx = LineageParser.MulDivContext(self, LineageParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 16
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 17
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==1 or _la==2):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 18
                        self.expr(7)
                        pass

                    elif la_ == 2:
                        localctx = LineageParser.AddSubContext(self, LineageParser.ExprContext(self, _parentctx, _parentState))
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expr)
                        self.state = 19
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 20
                        localctx.op = self._input.LT(1)
                        _la = self._input.LA(1)
                        if not(_la==3 or _la==4):
                            localctx.op = self._errHandler.recoverInline(self)
                        else:
                            self._errHandler.reportMatch(self)
                            self.consume()
                        self.state = 21
                        self.expr(6)
                        pass

             
                self.state = 26
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class IfExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IF(self):
            return self.getToken(LineageParser.IF, 0)

        def condition(self):
            return self.getTypedRuleContext(LineageParser.ConditionContext,0)


        def THEN(self):
            return self.getToken(LineageParser.THEN, 0)

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LineageParser.ExprContext)
            else:
                return self.getTypedRuleContext(LineageParser.ExprContext,i)


        def ELSE(self):
            return self.getToken(LineageParser.ELSE, 0)

        def getRuleIndex(self):
            return LineageParser.RULE_ifExpr

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIfExpr" ):
                return visitor.visitIfExpr(self)
            else:
                return visitor.visitChildren(self)




    def ifExpr(self):

        localctx = LineageParser.IfExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_ifExpr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 27
            self.match(LineageParser.IF)
            self.state = 28
            self.match(LineageParser.T__4)
            self.state = 29
            self.condition()
            self.state = 30
            self.match(LineageParser.T__5)
            self.state = 31
            self.match(LineageParser.THEN)
            self.state = 32
            self.expr(0)
            self.state = 33
            self.match(LineageParser.ELSE)
            self.state = 34
            self.expr(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConditionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser
            self.op = None # Token

        def expr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(LineageParser.ExprContext)
            else:
                return self.getTypedRuleContext(LineageParser.ExprContext,i)


        def getRuleIndex(self):
            return LineageParser.RULE_condition

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCondition" ):
                return visitor.visitCondition(self)
            else:
                return visitor.visitChildren(self)




    def condition(self):

        localctx = LineageParser.ConditionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_condition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 36
            self.expr(0)
            self.state = 37
            localctx.op = self._input.LT(1)
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 8064) != 0)):
                localctx.op = self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 38
            self.expr(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[0] = self.expr_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expr_sempred(self, localctx:ExprContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 6)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 5)
         




