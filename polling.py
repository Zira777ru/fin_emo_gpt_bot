import main



if __name__ == '__main__':
    main.executor.start_polling(main.dp, skip_updates=True, on_startup=main.on_startup)
