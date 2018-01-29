FROM python:2.7 AS build_base

RUN mkdir /pip_download
ADD ./setup/requirements/base.txt /pip_download/base/base.txt

RUN pip download -r /pip_download/base/base.txt -d /pip_download/base/
# Try to wheel everythig that may need dev libs
RUN cat /pip_download/base/base.txt | grep -v "^-e " | \
        pip wheel -r /dev/stdin \
        --no-index \
        --find-links /pip_download/base/ || echo "Warning: Not all wheels built"

# ----------------------------------------------------------
# End of base build stage
# ----------------------------------------------------------

FROM python:2.7 AS build_dev
# Dev requirements installed at runtime
ADD ./setup/requirements/dev.txt /pip_download/dev/dev.txt
RUN pip download -r /pip_download/dev/dev.txt -d /pip_download/dev/
RUN pip wheel -r /pip_download/dev/dev.txt \
        --no-index \
        --find-links /pip_download/dev/ || echo "Warning: Not all wheels built"
# Fix hold outs
RUN cd /pip_download/dev && pip wheel scandir
# ----------------------------------------------------------
# End of dev build stage
# ----------------------------------------------------------

FROM python:2.7 as install_base
COPY --from=build_base /pip_download/base /pip_download/base
RUN pip install --no-index --find-links=/pip_download/base -r /pip_download/base/base.txt
# Deal with edtiables 
RUN for x in `find /src/ -type f -name setup.py`; \
        do cd `dirname $x` && python $x install; \
     done
# ----------------------------------------------------------
# End of base build stage
# ----------------------------------------------------------

FROM python:2.7-slim

ENV USER django
ENV UID 1001
ENV ENV dev

# Copy already installed packages (done as root)
COPY --from=install_base /usr/local/lib/python2.7/site-packages/ /usr/local/lib/python2.7/site-packages/
# Add dev packages to be installed on entrypoint runtime
COPY ./setup/requirements/dev.txt /setup/dev.txt

RUN groupadd -g ${UID} -r ${USER} \
    && useradd -u ${UID} -r -g ${USER} ${USER} -d /src

ADD --chown=django:django /src/pysmve /src/pysmve

RUN chown ${USER}:${USER} /src
COPY --chown=django:django entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# ADD  https://github.com/neovim/neovim/releases/download/nightly/nvim.appimage /bin/vim
# RUN chmod +x vim

USER ${USER}
WORKDIR /src/pysmve

RUN mkdir /src/static

ENTRYPOINT [ "/entrypoint.sh" ]
