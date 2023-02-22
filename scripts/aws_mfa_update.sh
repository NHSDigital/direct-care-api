aws-mfa-update () {
        if [[ ${3} == "" ]]
        then
                echo "Usage: aws-mfa-update <account> <profile> <mfa token>"
        else
                aws --profile "${2:-default}" sts get-session-token --serial-number "arn:aws:iam::${1}:mfa/${2:-default}" --token-code "${3}" --duration-seconds 129600 > ~/.aws/credentials_tmp
                RETVAL=$?
                if [[ ${RETVAL} == 0 ]]
                then
                        echo "Credentials expire $(jq .Credentials.Expiration ~/.aws/credentials_tmp)"
                        aws configure --profile default set aws_access_key_id "$(jq -r .Credentials.AccessKeyId ~/.aws/credentials_tmp)"
                        aws configure --profile default set aws_secret_access_key "$(jq -r .Credentials.SecretAccessKey ~/.aws/credentials_tmp)"
                        aws configure --profile default set aws_session_token "$(jq -r .Credentials.SessionToken ~/.aws/credentials_tmp)"
                        rm -f ~/.aws/credentials_tmp
                else
                        echo "Getting credentials failed"
                fi
        fi
}
