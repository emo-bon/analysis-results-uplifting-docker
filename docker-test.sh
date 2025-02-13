#!/usr/bin/env bash

# get params or use defaults
dckr_cnt_nm=${1:-"emobon_arup"}
dckr_img_nm=${2:-"emobon_arup:latest"}

#build a temp space and fill it with the content
TMPDIR=$(mktemp -d) && echo "using TMPDIR=${TMPDIR}"
(cd ./tests/data/ && cp -r . ${TMPDIR})
cp ./tests/test-work.yml ${TMPDIR}/test-work.yml
tree ${TMPDIR}


#check if an image exists and build it if not
if [[ "$(docker images -q ${dckr_img_nm} 2> /dev/null)" == "" ]]; then
  echo "building the image"
  docker build -t ${dckr_img_nm} .
fi

#run the built container
docker run --rm \
  --name emo-bon_${dckr_cnt_nm} \
  --volume ${TMPDIR}:/rocrateroot \
  --env ARUP_WORK=test-work.yml \
  --env SAMPLE_MAT_ID='test_sm_id' \
  ${dckr_img_nm}

#verify the output
test -f ${TMPDIR}/test-output.ttl || (echo "mising output file" && exit 1)
test -f ${TMPDIR}/test-output2.ttl || (echo "missing 2nd output file" && exit 1)
diff ${TMPDIR}/test-output.ttl ${TMPDIR}/test-output2.ttl || (echo "unexpected diff between output files" && exit 1)
ttl=$(which ttl)  # look for ttl validator
if [[ -x "${ttl}" ]]; then
  ${ttl} ${TMPDIR}/test-output.ttl || (echo "ttl validation failed" && exit 1)
  # no need to check the 2nd file, it is the same as the first
fi

#say bye and clean up
echo "test passed, cleaning up"
rm -rf ${TMPDIR}
exit 0