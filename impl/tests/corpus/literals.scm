(test-suite "literals"

  (test-case "true literal"
    :program
      "true"
    :untyped-ast
      (BoolLiteral :value True)
    :typed-ast
      (BoolLiteral Bool)
    :eval
      "True")

  (test-case "false literal"
    :program
      "false"
    :untyped-ast
      (BoolLiteral :value False)
    :typed-ast
      (BoolLiteral Bool)
    :eval
      "False")

  (test-case "int literal"
    :program
      "123"
    :untyped-ast
      (IntLiteral :value "123")
    :typed-ast
      (IntLiteral Int)
    :eval
      "123")

  (test-case "negative signed int literal"
    :program
      "-1"
    :untyped-ast
      (UnaryOp
        :op "-"
        :operand (IntLiteral :value "1"))
    :typed-ast
      (UnaryOp Int
        :operand (IntLiteral Int))
    :eval
      "-1")

  (test-case "positive signed int literal"
    :program
      "+1"
    :untyped-ast
      (UnaryOp
        :op "+"
        :operand (IntLiteral :value "1"))
    :typed-ast
      (UnaryOp Int
        :operand (IntLiteral Int))
    :eval
      "1")
)
