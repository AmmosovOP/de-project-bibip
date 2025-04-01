import os
from typing import Optional
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class CarService:
    def __init__(self, root_directory_path: str) -> None:
        self.root_directory_path = root_directory_path
        os.makedirs(root_directory_path, exist_ok=True)
        self._init_file("cars.txt")
        self._init_file("models.txt")
        self._init_file("sales.txt")
        self._init_file("cars_index.txt")
        self._init_file("models_index.txt")
        self._init_file("sales_index.txt")
    def _init_file(self, filename: str) -> None:
        """Создаёт пустой файл, если его нет."""
        filepath = os.path.join(self.root_directory_path, filename)
        if not os.path.exists(filepath):
            open(filepath, 'w').close()

    # Задание 1. Сохранение автомобилей и моделей
    def add_model(self, model: Model) -> Model:
       
        index_file = os.path.join(self.root_directory_path, "models_index.txt")
        data_file = os.path.join(self.root_directory_path, "models.txt")
               
        index = self._read_index(index_file)
                
        if any(model.id == int(key) for key, _ in index):
            raise ValueError(f"Модель с ID {model.id} уже существует!")
                
        data_line = f"{model.id}|{model.name}|{model.brand}".ljust(500) + "\n"
        
        with open(data_file, 'a') as f:
            f.write(data_line)
        
        line_number = self._count_lines(data_file) - 1
        
        self._update_index(index_file, str(model.id), line_number)
        
        return model

    def _read_index(self, index_file: str) -> list[tuple[str, int]]:
        try:
            with open(index_file, 'r') as f:
                lines = f.readlines()
            return [(line.split('|')[0], int(line.split('|')[1])) for line in lines]
        except FileNotFoundError:
            return []

    def _update_index(self, index_file: str, key: str, line_number: int) -> None:
        index = self._read_index(index_file)
        index.append((key, line_number))
        index.sort(key=lambda x: x[0])  # Сортируем по ключу
        
        with open(index_file, 'w') as f:
            for k, ln in index:
                f.write(f"{k}|{ln}\n")

    def _count_lines(self, filepath: str) -> int:
        
        with open(filepath, 'r') as f:
            return sum(1 for _ in f)

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        index_file = os.path.join(self.root_directory_path, "cars_index.txt")
        data_file = os.path.join(self.root_directory_path, "cars.txt")
        
        index = self._read_index(index_file)
        
        if any(car.vin == key for key, _ in index):
            raise ValueError(f"Автомобиль с VIN {car.vin} уже существует!")
        data_line = f"{car.vin}|{car.model}|{car.price}|{car.date_start}|{car.status}".ljust(500) + "\n"
        
        with open(data_file, 'a') as f:
            f.write(data_line)
        
        line_number = self._count_lines(data_file) - 1
        self._update_index(index_file, car.vin, line_number)
        
        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        sales_index_file = os.path.join(self.root_directory_path, "sales_index.txt")
        sales_file = os.path.join(self.root_directory_path, "sales.txt")

        sales_index = self._read_index(sales_index_file)
        if any(sale.sales_number == key for key, _ in sales_index):
            raise ValueError(f"Продажа с номером {sale.sales_number} уже существует!")

        sales_line = f"{sale.sales_number}|{sale.car_vin}|{sale.cost}|{sale.sales_date}".ljust(500) + "\n"

        with open(sales_file, 'a') as f:
            f.write(sales_line)

        line_number = self._count_lines(sales_file) - 1
        self._update_index(sales_index_file, sale.sales_number, line_number)

        cars_index_file = os.path.join(self.root_directory_path, "cars_index.txt")
        cars_file = os.path.join(self.root_directory_path, "cars.txt")

        cars_index = self._read_index(cars_index_file)
        car_line_number = None
        
        for vin, line_num in cars_index:
            if vin == sale.car_vin:
                car_line_number = line_num
                break
        
        if car_line_number is None:
            raise ValueError(f"Автомобиль с VIN {sale.car_vin} не найден!")
        
        with open(cars_file, 'r+') as f:
            f.seek(car_line_number * 501) 
            car_line = f.read(500).strip()
        
        vin, model, price, date_start, status = car_line.split('|')
        
        updated_car_line = f"{vin}|{model}|{price}|{date_start}|sold".ljust(500) + "\n"

        with open(cars_file, 'r+') as f:
            f.seek(car_line_number * 501)
            f.write(updated_car_line)

        return Car(
            vin=vin,
            model=int(model),
            price=float(price),
            date_start=date_start,
            status="sold"
        )

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        
        cars_file = os.path.join(self.root_directory_path, "cars.txt")
        available_cars = []

        with open(cars_file, 'r') as f:
            for line in f:
                line = line.strip()  
                if not line:
                    continue 

                parts = line.split('|')
                if len(parts) != 5:
                    continue 
                
                vin, model, price, date_start, car_status = parts
            
                if car_status == status.value:
                    available_cars.append(
                        Car(
                            vin=vin,
                            model=int(model),
                            price=float(price),
                            date_start=date_start,
                            status=car_status
                        )
                    )

        available_cars.sort(key=lambda car: car.vin)
        
        return available_cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:

        cars_index_file = os.path.join(self.root_directory_path, "cars_index.txt")
        cars_file = os.path.join(self.root_directory_path, "cars.txt")
        
        cars_index = self._read_index(cars_index_file)
        car_line_number = None

        for v, line_num in cars_index:
            if v == vin:
                car_line_number = line_num
                break
        
        if car_line_number is None:
            return None  

        with open(cars_file, 'r') as f:
            f.seek(car_line_number * 501)
            car_line = f.read(500).strip()

        vin, model_id, price, date_start, status = car_line.split('|')
        
       
        models_index_file = os.path.join(self.root_directory_path, "models_index.txt")
        models_file = os.path.join(self.root_directory_path, "models.txt")
        
        models_index = self._read_index(models_index_file)
        model_line_number = None

        for m_id, line_num in models_index:
            if m_id == model_id:
                model_line_number = line_num
                break
        
        if model_line_number is None:
            raise ValueError(f"Модель с ID {model_id} не найдена!")

        with open(models_file, 'r') as f:
            f.seek(model_line_number * 501)
            model_line = f.read(500).strip()

        _, model_name, model_brand = model_line.split('|')

        sales_date = None
        sales_cost = None
        
        if status == "sold":
            sales_file = os.path.join(self.root_directory_path, "sales.txt")
            
            with open(sales_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    sales_number, car_vin, cost, sale_date = line.split('|')
                    
                    if car_vin == vin:
                        sales_date = sale_date
                        sales_cost = float(cost)
                        break

        return CarFullInfo(
            vin=vin,
            car_model_name=model_name,  
            car_model_brand=model_brand,  
            price=float(price),
            date_start=date_start,
            status=status,
            sales_date=sales_date,
            sales_cost=sales_cost
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        
        cars_index_file = os.path.join(self.root_directory_path, "cars_index.txt")
        cars_file = os.path.join(self.root_directory_path, "cars.txt")
        
        cars_index = self._read_index(cars_index_file)
        car_line_number = None
        
        for i, (v, line_num) in enumerate(cars_index):
            if v == vin:
                car_line_number = line_num
                break
        
        if car_line_number is None:
            raise ValueError(f"Автомобиль с VIN {vin} не найден!")        

        with open(cars_file, 'r+') as f:
            f.seek(car_line_number * 501)
            car_line = f.read(500).strip()
        _, model, price, date_start, status = car_line.split('|')
        updated_car_line = f"{new_vin}|{model}|{price}|{date_start}|{status}".ljust(500) + "\n"
        
        # 4. Перезаписываем строку
        with open(cars_file, 'r+') as f:
            f.seek(car_line_number * 501)
            f.write(updated_car_line)

        del cars_index[i]
        bisect.insort(cars_index, (new_vin, car_line_number))  

        with open(cars_index_file, 'w') as f:
            for v, line_num in cars_index:
                f.write(f"{v}|{line_num}\n")

        return Car(
            vin=new_vin,
            model=int(model),
            price=float(price),
            date_start=date_start,
            status=status
        )

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:

        sales_index_file = os.path.join(self.root_directory_path, "sales_index.txt")
        sales_file = os.path.join(self.root_directory_path, "sales.txt")
        cars_index_file = os.path.join(self.root_directory_path, "cars_index.txt")
        cars_file = os.path.join(self.root_directory_path, "cars.txt")


        sales_index = self._read_index(sales_index_file)
        sale_line_number = None
        sale_data = None

        for i, (s_num, line_num) in enumerate(sales_index):
            if s_num == sales_number:
                sale_line_number = line_num
                break

        if sale_line_number is None:
            raise ValueError(f"Продажа с номером {sales_number} не найдена!")
        with open(sales_file, 'r') as f:
            f.seek(sale_line_number * 501)
            sale_line = f.read(500).strip()

        parts = sale_line.split('|')
        if len(parts) < 4:
            raise ValueError("Некорректный формат записи о продаже!")

        sales_number, car_vin, cost, sales_date = parts[:4]
        is_deleted = parts[4] if len(parts) > 4 else "0"

        if is_deleted == "1":
            raise ValueError(f"Продажа {sales_number} уже отменена!")

        updated_sale_line = f"{sales_number}|{car_vin}|{cost}|{sales_date}|1".ljust(500) + "\n"

        with open(sales_file, 'r+') as f:
            f.seek(sale_line_number * 501)
            f.write(updated_sale_line)

        cars_index = self._read_index(cars_index_file)
        car_line_number = None

        for vin, line_num in cars_index:
            if vin == car_vin:
                car_line_number = line_num
                break

        if car_line_number is None:
            raise ValueError(f"Автомобиль с VIN {car_vin} не найден!")

        with open(cars_file, 'r+') as f:
            f.seek(car_line_number * 501)
            car_line = f.read(500).strip()

        vin, model, price, date_start, status = car_line.split('|')

        if status != "sold":
            raise ValueError(f"Автомобиль {vin} не продан, отмена продажи невозможна!")

        updated_car_line = f"{vin}|{model}|{price}|{date_start}|available".ljust(500) + "\n"

        with open(cars_file, 'r+') as f:
            f.seek(car_line_number * 501)
            f.write(updated_car_line)

        return Car(
            vin=vin,
            model=int(model),
            price=float(price),
            date_start=date_start,
            status="available"
        )

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        sales_file = os.path.join(self.root_directory_path, "sales.txt")
        cars_file = os.path.join(self.root_directory_path, "cars.txt")
        models_file = os.path.join(self.root_directory_path, "models.txt")
        models_index_file = os.path.join(self.root_directory_path, "models_index.txt")


        model_sales = {}

        with open(sales_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) < 5: 
                    continue
                
                sales_number, car_vin, _, _, is_deleted = parts
                if is_deleted == "1":
                    continue

                model_id = car.model
                model_sales[model_id] = model_sales.get(model_id, 0) + 1

        sorted_models = sorted(
            model_sales.items(),
            key=lambda x: (-x[1], -self._get_avg_model_price(x[0])), 
        )[:3] 

        top_models = []
        models_index = self._read_index(models_index_file)

        for model_id, sales_count in sorted_models:
            model_line_number = None
            for m_id, line_num in models_index:
                if m_id == str(model_id):
                    model_line_number = line_num
                    break

            if model_line_number is None:
                continue  

          
            with open(models_file, 'r') as f:
                f.seek(model_line_number * 501)
                model_line = f.read(500).strip()

            _, name, brand = model_line.split('|')
            top_models.append(
                ModelSaleStats(
                    car_model_name=name,
                    brand=brand,
                    sales_count=sales_count
                )
            )

        return top_models

    def _get_car_by_vin(self, vin: str) -> Optional[Car]:
        
        cars_index_file = os.path.join(self.root_directory_path, "cars_index.txt")
        cars_file = os.path.join(self.root_directory_path, "cars.txt")

        cars_index = self._read_index(cars_index_file)
        car_line_number = None

        for v, line_num in cars_index:
            if v == vin:
                car_line_number = line_num
                break

        if car_line_number is None:
            return None

        with open(cars_file, 'r') as f:
            f.seek(car_line_number * 501)
            car_line = f.read(500).strip()

        vin, model, price, date_start, status = car_line.split('|')
        return Car(
            vin=vin,
            model=int(model),
            price=float(price),
            date_start=date_start,
            status=status
        )

    def _get_avg_model_price(self, model_id: int) -> float:
        
        cars_file = os.path.join(self.root_directory_path, "cars.txt")
        prices = []

        with open(cars_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                vin, m_id, price, _, _ = line.split('|')
                if int(m_id) == model_id:
                    prices.append(float(price))

        return sum(prices) / len(prices) if prices else 0
