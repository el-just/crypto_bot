class Channel():
    __data_snapshot = None

    def __init__(self,
            connection,
            name=None,
            type_=None):
        self.name = name
        self.type_ = type_
        self.__connection = connection

        self.__data_snapshot = pd.DataFrame()

    async def send(self, message, reciever):
        if self.type_ == 'frame':
            message = (message if isinstance(message, pd.DataFrame) else
                    pd.DataFrame().append(message))

            combined = message.combine_first(self.__data_snapshot)
            message = self.__get_diff(self.__data_snapshot, combined)

            if not message.empty:
                self.__data_snapshot = combined
            else:
                message = None

        if message is not None:
            await reciever._recieve_message(
                    message,
                    reciever.connections.loc[id(self.__connection), :],
                    channel=self.name)

    def __get_diff(self, old, new):
        diff = pd.DataFrame()
        concat = old.append(new).drop_duplicates()

        if self.__data_snapshot.shape[0] != concat.shape[0]:
            pre_diff = concat.iloc[old.shape[0]:, :]

            for idx, row in pre_diff.iterrows():
                for column in row.index.values:
                    if idx in old.index and column in old.columns:
                        if row.at[column] == old.loc[idx, :].at[column]:
                            row.at[column] = None

            diff = pre_diff.dropna(how='all')

        return diff
