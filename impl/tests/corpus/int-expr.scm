(test-suite "int expression"

  (test-case "addition with positive int"
    :program
      "1+2"
    :untyped-ast
      (Term
        :left (IntLiteral :value 1)
        :op "+"
        :right (IntLiteral :value 2))
    :typed-ast
      (Term Int
        :left (IntLiteral Int)
        :right (IntLiteral Int))
    :eval
      3)

  (test-case "addition with negative int right"
    :program
      "1+-2"
    :untyped-ast
      (Term
        :left (IntLiteral :value 1)
        :op "+"
        :right
          (UnaryOp
            :op "-"
            :operand (IntLiteral :value 2)))
    :typed-ast
      (Term Int
        :left (IntLiteral Int)
        :right 
          (UnaryOp Int
            :operand (IntLiteral Int)))
    :eval
      "-1")

  (test-case "addition with negative int left"
    :program
      "-1+2"
    :untyped-ast
      (Term
        :left
          (UnaryOp
            :op "-"
            :operand (IntLiteral :value 1))
        :op "+"
        :right (IntLiteral :value 2))
    :typed-ast
      (Term Int
        :left 
          (UnaryOp Int
            :operand (IntLiteral Int))
        :right (IntLiteral Int))
    :eval
      "1")

  (test-case "addition with negative int both"
    :program
      "-1+-2"
    :untyped-ast
      (Term
        :left
          (UnaryOp
            :op "-"
            :operand (IntLiteral :value 1))
        :op "+"
        :right
          (UnaryOp
            :op "-"
            :operand (IntLiteral :value 2)))
    :typed-ast
      (Term Int
        :left 
          (UnaryOp Int
            :operand (IntLiteral Int))
        :right
          (UnaryOp Int
            :operand (IntLiteral Int)))
    :eval
      "-3")

  (test-case "subtraction with positive int"
    :program
      "1-2"
    :untyped-ast
      (Term
        :left (IntLiteral :value 1)
        :op "-"
        :right (IntLiteral :value 2))
    :typed-ast
      (Term Int
        :left (IntLiteral Int)
        :right (IntLiteral Int))
    :eval
      "-1")

  (test-case "subtraction with negative int right"
    :program
      "1--2"
    :untyped-ast
      (Term
        :left (IntLiteral :value 1)
        :op "-"
        :right
          (UnaryOp
            :op "-"
            :operand (IntLiteral :value 2)))
    :typed-ast
      (Term Int
        :left (IntLiteral Int)
        :right 
          (UnaryOp Int
            :operand (IntLiteral Int)))
    :eval
      "3")

  (test-case "subtraction with negative int left"
    :program
      "-1-2"
    :untyped-ast
      (Term
        :left
          (UnaryOp
            :op "-"
            :operand (IntLiteral :value 1))
        :op "-"
        :right (IntLiteral :value 2))
    :typed-ast
      (Term Int
        :left 
          (UnaryOp Int
            :operand (IntLiteral Int))
        :right (IntLiteral Int))
    :eval
      "-3")

  (test-case "subtraction with negative int both"
    :program
      "-1--2"
    :untyped-ast
      (Term
        :left
          (UnaryOp
            :op "-"
            :operand (IntLiteral :value 1))
        :op "-"
        :right
          (UnaryOp
            :op "-"
            :operand (IntLiteral :value 2)))
    :typed-ast
      (Term Int
        :left 
          (UnaryOp Int
            :operand (IntLiteral Int))
        :right
          (UnaryOp Int
            :operand (IntLiteral Int)))
    :eval
      "1")

  (test-case "unary op on bool error"
    :program
      "-true"
    :untyped-ast
      (UnaryOp
        :op "-"
        :operand (BoolLiteral :value True))
    :error
      (InvalidOperationError
        :message "Invalid operation '-' for type 'Bool'"
        :span (Span :start "1:1" :end "1:6")
        :operator ("-" (Span :start "1:1" :end "1:2"))
        :operands (
          ("Bool" (Span :start "1:2" :end "1:6")))))
)
