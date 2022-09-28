# qrCodeImageSorterGUI
GUI interface for the [qrCodeImageSorter](https://github.com/jonpecar/qrCodeImageSorter) repository.

## Note around build tests:

There appears to be an issue with joining the threaded tests when running in GitHub actions on Python versions 3.7 & 3.10. 
The tests will consistently fail on trying to rejoin the Thread. This is not reproduceable on a local machine. 
As such build tests are only running on 3.8 & 3.9 until this is resolved.
