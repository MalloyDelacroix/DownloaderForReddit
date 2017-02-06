from DFR_Updater.Updater import Updater


def main():
    updater = Updater()
    updater.download_update()
    # updater.delete_old_files()
    updater.replace_with_new_version()

if __name__ == '__main__':
    main()
