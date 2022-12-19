import json
from algosdk import account, mnemonic
from algosdk.v2client import algod
from algosdk.future.transaction import wait_for_confirmation, AssetConfigTxn, PaymentTxn, AssetTransferTxn, calculate_group_id, AssetFreezeTxn


algod_client = algod.AlgodClient("", "https://testnet-api.algonode.cloud")
params = algod_client.suggested_params()

mnemonic1 = "symptom grass lunar labor oil client clump soccer conduct element cradle destroy height canvas replace dinner sport toe cattle point nose idle defense above flower"
private_key1 = mnemonic.to_private_key(mnemonic1)
account1 = account.address_from_private_key(private_key1)

mnemonic2 = "still simple model depart acoustic unknown grass sad acoustic flat trim ranch gossip tip grunt bread wheat size slogan spread pride forest dog absorb wife"
private_key2 = mnemonic.to_private_key(mnemonic2)
account2 = account.address_from_private_key(private_key2)

mnemonic3 = "cheese rural toss fiber finish join ostrich train minute visa pigeon state tuition noise enemy immense clutch city traffic industry adult cargo insect able husband"
private_key3 = mnemonic.to_private_key(mnemonic3)
account3 = account.address_from_private_key(private_key3)


""" Fund account 1 from https://dispenser.testnet.aws.algodev.network/, send some funds to account to cover account 2 fees """
def fund_accounts():
    print("Funding accounts to cover fees")
    txn1 = PaymentTxn(account1, params, account2, 10000)
    txn2 = PaymentTxn(account1, params, account3, 10000)

    gid = calculate_group_id([txn1, txn2])

    txn1.group = gid
    txn2.group = gid

    signed_txn1 = txn1.sign(private_key1)
    signed_txn2 = txn2.sign(private_key1)

    signed_group = [signed_txn1, signed_txn2]

    try:
        tx_id = algod_client.send_transactions(signed_group)
        print(f"TX ID {tx_id}")
        confirmed_txn = wait_for_confirmation(algod_client, tx_id, 4)
        print(f"TX ID {tx_id}")
        print(f"Transaction confirmed in {confirmed_txn['confirmed-round']} rounds")
    except Exception as e:
        print(e)


def asset_info(algodclient, account, assetid):
    account_info = algodclient.account_info(account)
    idx = 0
    for my_account_info in account_info['created-assets']:
        scrutinized_asset = account_info['created-assets'][idx]
        idx += 1       
        if scrutinized_asset['index'] == assetid:
            print("Asset ID: {}".format(scrutinized_asset['index']))
            print(json.dumps(my_account_info['params'], indent=4))
            break


def asset_holding_info(algod_client, account, assetid):
    account_info = algod_client.account_info(account)
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx += 1
        if scrutinized_asset['asset-id'] == assetid:
            print(f"Asset ID {scrutinized_asset['asset-id']}")
            print(f"{json.dumps(scrutinized_asset, indent=4)}")
            break

asset_id = None

def create_asset():
    print("Create Asset")
    global asset_id

    txn = AssetConfigTxn(
        sender=account1, 
        sp=params, 
        total=1000, 
        default_frozen=False, 
        unit_name="Tokenza", 
        asset_name="tza", 
        manager=account2, 
        reserve=account2, 
        freeze=account2, 
        clawback=account2, 
        url="", 
        decimals=0
    )

    signed_txn = txn.sign(private_key1)

    try:
        tx_id = algod_client.send_transaction(signed_txn)
        print(f"Transaction ID {tx_id}")
        confirmed_txn = wait_for_confirmation(algod_client, tx_id, 4)
        print(f"Transaction ID {tx_id}")
        print(f"Confirmed transaction in {confirmed_txn['confirmed-round']} rounds")
    except Exception as e:
        print(e)

    print(f"Transaction information {json.dumps(confirmed_txn, indent=4)}")

    try:
        ptx = algod_client.pending_transaction_info(tx_id)
        asset_id = ptx["asset-index"]
        
        asset_info(algod_client, account1, asset_id)
        asset_holding_info(algod_client, account1, asset_id)
    except Exception as e:
        print(e)


def modify_asset():
    print("Modify Asset")
    txn = AssetConfigTxn(
        sender=account2, 
        sp=params, 
        index=asset_id, 
        manager=account1, 
        reserve=account2, 
        freeze=account2, 
        clawback=account2
    )

    signed_txn = txn.sign(private_key2)

    try:
        tx_id = algod_client.send_transaction(signed_txn)
        print(f"Signed transaction with TX ID {tx_id}")
        
        confirmed_txn = wait_for_confirmation(algod_client, tx_id, 4)
        print(f"TX ID {tx_id}")
        print(f"Result confirmed in {confirmed_txn['confirmed-round']} rounds")
    except Exception as err:
        print(err)

    asset_info(algod_client, account1, asset_id)


def receive_asset():
    print("Receive Asset")
    account_info = algod_client.account_info(account3)
    holding = None
    idx = 0
    for my_account_info in account_info['assets']:
        scrutinized_asset = account_info['assets'][idx]
        idx += 1
        if scrutinized_asset['asset-id'] == asset_id:
            holding = True
            break
    if not holding:
        txn = AssetTransferTxn(
            sender=account3, 
            sp=params, 
            receiver=account3, 
            amt=0, 
            index=asset_id
        )
        signed_txn = txn.sign(private_key3)
        try:
            tx_id = algod_client.send_transaction(signed_txn)
            print(f"Signed transaction with TX ID {tx_id}")
            confirmed_txn = wait_for_confirmation(algod_client, tx_id, 4)
            print(f"TX ID {tx_id}")
            print(f"Result confirmed in {confirmed_txn['confirmed-round']} rounds")
        except Exception as e:
            print(e)
        asset_holding_info(algod_client, account3, asset_id)


def transfer_asset():
    print("Transfer Asset")
    txn = AssetTransferTxn(
        sender=account1,
        sp=params,
        receiver=account3,
        amt=10,
        index=asset_id
    )

    signed_txn = txn.sign(private_key1)

    try:
        tx_id = algod_client.send_transaction(signed_txn)
        print(f"Signed transaction with TX ID {tx_id}")

        confirmed_txn = wait_for_confirmation(algod_client, tx_id)
        print(f"TX ID {tx_id}")
        print(f"Result confirmed in {confirmed_txn['confirmed-round']} rounds")
    except Exception as e:
        print(e)

    asset_holding_info(algod_client, account3, asset_id)


def freeze_asset():
    print("Freeze Asset")
    txn = AssetFreezeTxn(
        sender=account2,
        sp=params,
        index=asset_id,
        target=account3,
        new_freeze_state=True
    )

    signed_txn = txn.sign(private_key2)

    try:
        tx_id = algod_client.send_transaction(signed_txn)
        print(f"Signed transaction with TX ID {tx_id}")

        confirmed_txn = wait_for_confirmation(algod_client, tx_id)
        print(f"TX ID {tx_id}")
        print(f"Result confirmed in {confirmed_txn['confirmed-round']} rounds")
    except Exception as e:
        print(e)

    asset_holding_info(algod_client, account3, asset_id)


def revoke_asset():
    print("Revoke Asset")
    txn = AssetTransferTxn(
        sender=account2,
        sp=params,
        receiver=account1,
        amt=10,
        index=asset_id,
        revocation_target=account3
    )

    signed_txn = txn.sign(private_key2)

    try:
        tx_id = algod_client.send_transaction(signed_txn)
        print(f"Transaction signed with {tx_id}")

        confirmed_txn = wait_for_confirmation(algod_client, tx_id)
        print(f"TX ID {tx_id}")
        print(f"Result confirmed in {confirmed_txn['confirmed-round']} rounds")
    except Exception as e:
        print(e)

    print("Account 3")
    asset_holding_info(algod_client, account3, asset_id)

    print("Account 1")
    asset_holding_info(algod_client, account3, asset_id)


def destroy_asset():
    txn = AssetConfigTxn(
        sender=account1,
        sp=params,
        index=asset_id,
        strict_empty_address_check=False
    )
    
    signed_txn = txn.sign(private_key1)

    try:
        tx_id = algod_client.send_transaction(signed_txn)
        print(f"Transaction signed with ID {tx_id}")

        confirmed_txn = wait_for_confirmation(algod_client, tx_id)
        print(f"TX ID {tx_id}")
        print(f"Result confirmed in {confirmed_txn['confirmed-round']} rounds")
    except Exception as e:
        print(e)

    try:
        asset_holding_info(algod_client, account1, asset_id)
        asset_info(algod_client, account1, asset_id)
    except Exception as e:
        print(e) 


# fund_accounts()
create_asset()
modify_asset()
receive_asset()
transfer_asset()
freeze_asset()
revoke_asset()
destroy_asset()
