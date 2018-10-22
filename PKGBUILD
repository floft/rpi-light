# Maintainer: Garrett <floft.net/contact>
pkgname=rpi-lights-git
pkgver=1
pkgrel=1
pkgdesc="Control my lights with my Raspberry Pi"
arch=('any')
url="https://github.com/floft/rpi-lights"
license=('ISC')
depends=('python-tornado' 'python-yaml' 'python-pyserial')
makedepends=('git')
backup=('etc/lights.yaml')
source=()
md5sums=()

pkgver() {
    cd "$startdir"
    printf "r%s.%s" "$(git rev-list --count HEAD)" "$(git rev-parse --short HEAD)"
}

package() {
    cd "$startdir"
    mkdir -p "${pkgdir}/etc" "${pkgdir}/usr/bin" "${pkgdir}/usr/lib/systemd/system"
    install -Dm644 "config.yaml" "${pkgdir}/etc/lights.yaml"
    install -Dm755 "lights.py" "${pkgdir}/usr/bin/lights"
    install -Dm644 "lights.service" "${pkgdir}/usr/lib/systemd/system"
}
