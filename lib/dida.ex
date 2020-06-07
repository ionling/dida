defmodule API do
  @api "https://api.dida365.com/api/v2"
  @cookie_path ".cookie"

  def init do
    cookie = File.read!(@cookie_path)
    :ets.new(:cache, [:set, :named_table])
    :ets.insert(:cache, {"cookie", String.trim(cookie)})
  end

  @spec get_cookie() :: keyword()
  defp get_cookie do
    [{"cookie", cookie}] = :ets.lookup(:cache, "cookie")
    [cookie: cookie]
  end

  @doc "List all tasks"
  @spec list(boolean(), function()) :: list
  def list(shuffle \\ false, filter \\ fn _ -> true end) do
    url = "#{@api}/batch/check/0"
    r = HTTPoison.get!(url, get_cookie())

    tasks =
      case Jason.decode(r.body) do
        {:ok, data} ->
          data["syncTaskBean"]["update"] |> Enum.filter(filter)

        {:error, e} ->
          IO.inspect(e)
          []
      end

    if shuffle do
      tasks |> Enum.shuffle()
    else
      tasks
    end
  end

  @spec delete(String.t(), String.t()) :: boolean()
  def delete(project_id, task_id) do
    url = "#{@api}/batch/task"
    headers = get_cookie() ++ ["content-type": "application/json;charset=UTF-8"]

    body =
      Jason.encode!(%{
        "add" => [],
        "update" => [],
        "delete" => [%{"projectId" => project_id, "taskId" => task_id}]
      })

    r = HTTPoison.post!(url, body, headers)
    r.status_code == 200
  end
end

defmodule DB do
  def init_db do
    pid = gen_server()
    Sqlitex.Server.exec(pid, "CREATE TABLE task(title TEXT, content TEXT);")
  end

  def gen_server do
    {:ok, pid} = Sqlitex.Server.start_link("db")
    pid
  end

  def insert(pid, title, content) do
    Sqlitex.Server.exec(pid, "INSERT INTO task VALUES ('#{title}', '#{content}')")
  end
end

defmodule App do
  alias IO.ANSI

  def archive(tasks) do
    pid = DB.gen_server()

    Enum.each(tasks, fn x ->
      IO.puts("New item:")
      title = x["title"]
      content = Map.get(x, "content", "")
      items_str = x["items"] |> Enum.map(fn y -> y["title"] end) |> Enum.join(" | ")
      IO.puts("\tTitle: " <> title)
      IO.puts("\tContent: " <> content)
      IO.puts("\tItems: " <> items_str)
      input = IO.gets("\tArchive/Delete/Skip it? (a/d/s) ")
      IO.write("\t")

      case input |> String.trim_trailing() |> String.downcase() do
        "a" ->
          :ok = DB.insert(pid, title, content)

          if API.delete(x["projectId"], x["id"]) do
            IO.puts(ANSI.green() <> "Archived" <> ANSI.reset())
          else
            IO.puts("Error deleting")
          end

        "d" ->
          if API.delete(x["projectId"], x["id"]) do
            IO.puts(ANSI.red() <> "Deleted" <> ANSI.reset())
          else
            IO.puts("Error deleting")
          end

        "m" ->
          API.done(x)
          IO.puts("Marked done")

        # TODO More handling
        _ ->
          IO.puts(ANSI.cyan() <> "Skipped" <> ANSI.reset())
      end

      IO.puts("")
    end)
  end

  def run do
    filter = fn x -> x["reminder"] == "" end
    API.list(true, filter) |> archive
  end
end

# DB.init_db

defmodule Dida do
  use Application

  def start(_type, _args) do
    Agent.start_link(fn ->
      API.init()
      App.run()
    end)
  end
end
