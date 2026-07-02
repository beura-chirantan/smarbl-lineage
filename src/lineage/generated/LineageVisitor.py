# Generated from Lineage.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .LineageParser import LineageParser
else:
    from LineageParser import LineageParser

# This class defines a complete generic visitor for a parse tree produced by LineageParser.

class LineageVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by LineageParser#MulDiv.
    def visitMulDiv(self, ctx:LineageParser.MulDivContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LineageParser#AddSub.
    def visitAddSub(self, ctx:LineageParser.AddSubContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LineageParser#Parens.
    def visitParens(self, ctx:LineageParser.ParensContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LineageParser#Var.
    def visitVar(self, ctx:LineageParser.VarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LineageParser#Const.
    def visitConst(self, ctx:LineageParser.ConstContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LineageParser#IfElseExpr.
    def visitIfElseExpr(self, ctx:LineageParser.IfElseExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LineageParser#ifExpr.
    def visitIfExpr(self, ctx:LineageParser.IfExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LineageParser#condition.
    def visitCondition(self, ctx:LineageParser.ConditionContext):
        return self.visitChildren(ctx)



del LineageParser