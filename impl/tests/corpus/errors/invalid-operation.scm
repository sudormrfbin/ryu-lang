(test-suite "invalid operation errors"

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