import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from keras.layers import Input, Embedding, Concatenate, Dense, GRU, Dropout, Reshape, Masking,TimeDistributed
from keras.models import Model
import matplotlib.pyplot as plt
from tensorflow.keras.optimizers import Adam


df = pd.read_csv('eCommerce.csv')
print(len(df))

df=df.dropna()
products_per_user = df.groupby('user_id')['product_id'].count().reset_index()

users_multiple_purchases = products_per_user[products_per_user['product_id'] > 1]

df = df[df['user_id'].isin(users_multiple_purchases['user_id'])]

# Encuentra la cantidad máxima de productos que ha comprado un usuario
max_products_purchased = 5
print(max_products_purchased)

products = df[['product_id', 'brand', 'category_code','price']].drop_duplicates(subset='product_id')

mean_price = df['price'].mean()
std_price = df['price'].std()
products['price']=(products['price']-mean_price)/std_price

n_products = len(products)
print(n_products)

map_id_user = {i:user for i, user in enumerate(df['user_id'].unique())}
n_users = len(map_id_user)

map_id_prod = {i+1: prod for i, prod in enumerate(products['product_id'])}
map_prod_id = {prod: i+1 for i, prod in enumerate(products['product_id'])}

unique_categories = products['category_code'].unique()
n_categories = len(unique_categories)
map_id_cat = {i+1: brand for i, brand in enumerate(unique_categories)}
map_cat_id = {brand: i+1 for i, brand in enumerate(unique_categories)}

unique_brands = products['brand'].unique()
n_brands = len(unique_brands)
map_id_brand = {i+1: brand for i, brand in enumerate(unique_brands)}
map_brand_id = {brand: i+1 for i, brand in enumerate(unique_brands)}

def generator(min_index, max_index, batch_size=64):
    """
    Generator que produce lotes de secuencias de compras.
    """
    products_count = df.groupby('product_id')['user_id'].count()
    max_frequency = products_count.max()
    product_weights = {pid: max_frequency / freq for pid, freq in products_count.items()}

    while True:
        seen_users = set()
        count = 0
        samples = [np.zeros((batch_size, max_products_purchased - 1)) for _ in range(4)]
        targets = np.zeros((batch_size, n_products))
        while count < batch_size:
            id = np.random.randint(min_index, max_index)
            user_id = map_id_user[id]
            if user_id in seen_users:
                continue
            seen_users.add(user_id)

            user_data = df[df['user_id'] == user_id]
            user_purchases = user_data['product_id'].tolist()
            if len(user_purchases) < 2:
                continue

            next_purchase = np.random.choice(range(1, len(user_purchases)))
            # start = 0
            if next_purchase>max_products_purchased-1:
                start = next_purchase-max_products_purchased+1
                purchases = np.array(user_purchases[start:next_purchase])
            else:
                purchases = np.array(user_purchases[:next_purchase])

            purchases_df = pd.DataFrame(purchases, columns=['id'])

            products_features = pd.merge(purchases_df, products, left_on='id',right_on='product_id', how='left')
            # print(f'Products features {products_features.size}')
            
            x_id = np.array([map_prod_id[prod] for prod in purchases])
            # print(f'x_id size {x_id.size}')

            brands_array = np.array(products_features['brand'].values)
            x_brand = np.array([map_brand_id[brand] for brand in brands_array])
            # print(f'x_brand.size before {x_brand.size}')
            
            cats_array = np.array(products_features['category_code'].values)
            x_cat = np.array([map_cat_id[cat] for cat in cats_array])

            x_price = np.array(products_features['price'].values)

            # print(f'comparison {len(purchases)} and {max_products_purchased-1}')
            if len(x_id) < max_products_purchased-1:
                x_id = np.pad(x_id, (0, max_products_purchased - len(x_id) - 1), 'constant')
                x_brand = np.pad(x_brand, (0, max_products_purchased - len(x_brand) - 1), 'constant')
                x_cat = np.pad(x_cat, (0, max_products_purchased - len(x_cat) - 1), 'constant')
                x_price = np.pad(x_price, (0, max_products_purchased - len(x_price) - 1), 'constant')
# print('x_brand.size')
            # print(x_brand.size)

            samples[0][count] = x_id
            samples[1][count] = x_brand
            samples[2][count] = x_cat
            samples[3][count] = x_price

            y = np.zeros((n_products,))
            y[map_prod_id[user_purchases[next_purchase]] - 1] = 1
            targets[count] = y

            count += 1

        yield tuple([np.array(sam, dtype=np.float32) for sam in samples]), np.array(targets, dtype=np.float32)


def create_tf_dataset(min_index, max_index, batch_size=64):
    return tf.data.Dataset.from_generator(
        lambda: generator(min_index, max_index, batch_size),
        output_signature=(
            (
                tf.TensorSpec(shape=(batch_size, max_products_purchased - 1), dtype=tf.float32),
                tf.TensorSpec(shape=(batch_size, max_products_purchased - 1), dtype=tf.float32),
                tf.TensorSpec(shape=(batch_size, max_products_purchased - 1), dtype=tf.float32),
                tf.TensorSpec(shape=(batch_size, max_products_purchased - 1), dtype=tf.float32),
            ),
            tf.TensorSpec(shape=(batch_size, n_products), dtype=tf.float32)
        )
    )

def predict_next_product(user_purchases, model):
    """
    Predice el próximo producto basado en las características de los productos comprados por el usuario.

    Args:
    - user_data: Datos del usuario con características de los productos comprados en formato de secuencia.
    - model: El modelo entrenado para hacer la predicción.
    - product_features: Diccionario que mapea product_id a características del producto.
    """

    products_features = products['product_id'].isin(user_purchases)

    x_id = pd.Series(user_purchases).map(map_prod_id).values
    x_brand = np.array(products.loc[products_features,'brand'].map(map_brand_id))
    x_cat = np.array(products.loc[products_features,'category_code'].map(map_cat_id))
    x_price = np.array(products.loc[products_features,'price'])
    

    return model.predict([x_id,x_brand,x_cat,x_price])


embedding_dim = 16
# Entrada para el ID
input_id = Input(shape=(max_products_purchased-1,))
embedding_id = Embedding(input_dim=n_products+1, output_dim=embedding_dim, mask_zero=True)(input_id)

# Entrada para otra característica (ej. categoría)
input_brand = Input(shape=(max_products_purchased-1,))
embedding_brand = Embedding(input_dim=n_brands+1, output_dim=embedding_dim, mask_zero=True)(input_brand)

# Entrada para otra característica (ej. categoría)
input_cat = Input(shape=(max_products_purchased-1,))
embedding_cat = Embedding(input_dim=n_categories+1, output_dim=embedding_dim, mask_zero=True)(input_cat)

input_price = Input(shape=(max_products_purchased-1,1))
price_dense = TimeDistributed(Dense(embedding_dim, activation='relu'))(input_price)

purchases = Concatenate()([embedding_id, embedding_brand, embedding_cat, price_dense])


# Concatenar los embeddings
# purchases = Concatenate()([embedding_id, embedding_brand, embedding_cat, Reshape((max_products_purchased-1, 1))(input_price)])

# Aplicar masking si se usa
masked_input = Masking(mask_value=0)(purchases)
gru_output = GRU(units=128)(masked_input)
dropout_output = Dropout(0.3)(gru_output)
output = Dense(units=n_products, activation='softmax')(dropout_output)

# Crear el modelo
optimizer = Adam(learning_rate=0.001)
model = Model(inputs=[input_id, input_brand, input_cat, input_price], outputs=output)
model.compile(optimizer=optimizer, loss='categorical_crossentropy', metrics=['accuracy'])

batch_size = 16

train_gen = create_tf_dataset(min_index=0, max_index=int(n_users*0.6), batch_size=batch_size)
val_gen = create_tf_dataset(min_index=int(n_users*0.6), max_index=int(n_users*0.9), batch_size=batch_size)
test_gen = create_tf_dataset(min_index=int(n_users*0.9), max_index=n_users, batch_size=batch_size)


steps_per_epoch = int(n_users*0.6)//batch_size
val_steps = int(n_users*0.3)//batch_size
test_steps = int (n_users*0.10)// batch_size

print(steps_per_epoch)
print(val_steps)

history = model.fit(train_gen,
                    steps_per_epoch=500,
                    epochs=10,
                    validation_data=val_gen,
                    validation_steps=500)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(acc) + 1)
plt.plot(epochs, acc, 'bo', label='Training acc')
plt.plot(epochs, val_acc, 'b', label='Validation acc')
plt.title('Training and validation accuracy')
plt.legend()
plt.figure()
plt.plot(epochs, loss, 'bo', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend()
plt.show()