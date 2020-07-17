
// Given a file size in bytes, return a size string
const FILE_SIZE_K = 1000
const FILE_SIZE_SUFFIX = 'B'
const FILE_SIZE_DECIMALS = 1
const FILE_SIZE_SEP = '\u00a0'
const FILE_SIZE_UNITS = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
const FILE_SIZE_UNITS_LAST_INDEX = FILE_SIZE_UNITS.length - 1

function fileSizeStr(size) {
    if (!size) {
        return ''
    }
    for (unit of FILE_SIZE_UNITS) {
        if (
            Math.abs(size) < FILE_SIZE_K
            || unit == FILE_SIZE_UNITS[FILE_SIZE_UNITS_LAST_INDEX]
        ) {
            return (
                (unit == '' ? size : size.toFixed(FILE_SIZE_DECIMALS))
                + FILE_SIZE_SEP
                + unit
                + (unit == '' ? 'bytes' : FILE_SIZE_SUFFIX)
            )
        }
        size = size / FILE_SIZE_K
    }
}

module.exports = {
    fileSizeStr
}
