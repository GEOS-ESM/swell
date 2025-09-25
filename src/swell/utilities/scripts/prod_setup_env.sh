unset R2D2_SERVER_HOST
unset R2D2_SERVER_PORT

export R2D2_USER=username
export R2D2_API_KEY=api_key
export R2D2_HOST=discover-gmao
export R2D2_COMPILER=intel

source venv_client/bin/activate

echo “  R2D2 Production environment:”
echo “  R2D2_API_KEY:  [set]”
echo “  R2D2_SERVER_HOST: $R2D2_SERVER_HOST '(should be empty)'”
echo “  R2D2_SERVER_PORT:  $R2D2_SERVER_PORT '(should be empty)'”
echo “  - Client should default to https://r2d2-api.jcsda.org”
echo “  R2D2_HOST: $R2D2_HOST”
echo “  R2D2_COMPILER: $R2D2_COMPILER”