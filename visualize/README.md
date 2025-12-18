# Metabase Visualization Setup

## Deploy Metabase to Minikube

Create and deploy the Metabase pod:

```bash
minikube kubectl -- apply -f metabase.yaml
```

## Access Metabase

Open the Metabase service:

```bash
minikube service metabase-service
```

## Configure Metabase

### MongoDB Connection Settings

Configure the following parameters to connect to MongoDB:

| Field | Value |
|-------|-------|
| Name | Bất động sản |
| Host | my-mongodb |
| Port | 27017 |
| Database name | real_estate_db |
| Username | root |
| Password | *Your MongoDB password* |

## Next Steps

1. Navigate to the Metabase dashboard URL
2. Set up your admin account
3. Add the MongoDB connection using the details above
4. Create visualizations from the real estate data
