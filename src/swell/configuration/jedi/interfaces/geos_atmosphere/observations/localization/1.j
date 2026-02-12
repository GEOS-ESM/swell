

for i in `ls *yaml`; do
  echo $i
  sed -e 's#lengthscale.*#lengthscale: 1000.e3#g'  \
      -e 's#max nobs.*#max nobs: 10000#g'  \
      $i > za
  diff $i za
  mv za $i
done
