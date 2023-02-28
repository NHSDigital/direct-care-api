FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y dist-upgrade \
    && apt-get -y install --no-install-recommends htop vim curl git build-essential \
    libffi-dev libssl-dev libxml2-dev libxslt1-dev libjpeg8-dev libbz2-dev \
    zlib1g-dev unixodbc unixodbc-dev libsecret-1-0 libsecret-1-dev libsqlite3-dev \
    openjdk-8-jdk jq apt-transport-https ca-certificates gnupg-agent \
    software-properties-common bash-completion python3-pip make libbz2-dev \
    libreadline-dev libsqlite3-dev wget llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev liblzma-dev netcat awscli

RUN wget -O /tmp/aws-sam-cli.zip https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip && \
    unzip /tmp/aws-sam-cli.zip -d /tmp/aws-sam-cli && \
    /tmp/aws-sam-cli/install 

USER vscode

# Install ASDF
RUN git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.9.0; \
    echo '. $HOME/.asdf/asdf.sh' >> ~/.bashrc; \
    echo '. $HOME/.asdf/completions/asdf.bash' >> ~/.bashrc; \
    echo 'source /workspaces/direct-care-api/scripts/aws_mfa_update.sh' >> ~/.bashrc

# Install ASDF plugins
RUN /home/vscode/.asdf/bin/asdf plugin add python; \
    /home/vscode/.asdf/bin/asdf plugin-add poetry https://github.com/asdf-community/asdf-poetry.git;



WORKDIR /workspaces/direct-care-api
ADD .tool-versions /workspaces/direct-care-api/.tool-versions

RUN /home/vscode/.asdf/bin/asdf install; \
    /home/vscode/.asdf/bin/asdf reshim python; \
    /home/vscode/.asdf/bin/asdf reshim poetry




