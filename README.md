# Сборка и запуск проекта

Для сборки должен быть установлен npm. 

    #на локали
    npm run build    
    python manage.py post-webpack

Данные для загрузки в базу надо заливать отдельно, не через GIT    
            
    # на сервере после деплоя   
    python manage.py collectstatic
    python manage.py migrate
    python manage.py seed
    python manage.py seed_icecat
    python manage.py attribute_statistics   
    python manage.py index


	catalog_categorytoproductattributerelation
	catalog_CategoryToProductAttributeRelation