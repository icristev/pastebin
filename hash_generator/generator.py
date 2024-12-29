from app.utils.hash_utils import generate_hashes


def main():
    # Генерация начальной пачки хэшей
    print("Генерация хэшей...")
    generate_hashes(batch_size=1000)
    print("Генерация завершена.")


if __name__ == "__main__":
    main()
